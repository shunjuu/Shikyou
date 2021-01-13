import os
import subprocess

from ayumi import Ayumi
from json import loads
from metsuke import Job
from typing import Iterable, List

# Note: Subprocess and rclone seem to handle correctly, unlike ffmpeg.

class ShikyouTimeoutException(Exception):
    pass

class ShikyouResponseException(Exception):
    pass

def _clean(title: str) -> str:
    if title.endswith("/"):
        return title[:-1]
    else:
        return title

def _run(command: Iterable[str]) -> str:
    # Subprocess passes signals properly to the ffmpeg child, so we can just run it as is.

    try:
        response = subprocess.run(command, capture_output=True, timeout=3600)
    except subprocess.TimeoutExpired:
        Ayumi.warning("Command expired by timeout, killing...")
        raise ShikyouResponseException()

    if response.returncode != 0:
        Ayumi.warning("Command caused return code of {}, returning None.".format(response.returncode))
        raise ShikyouResponseException()

    return response

def _check_exists(config: str, source: str, job: Job) -> bool:
    """
    Checks if the jobs exists under the source.
    Note: Does not validate under which path, just validates that jobs exists somewhere in:
    source/(...probably job.show)/job.episode
    """
    try:
        response = _run(["rclone",
                        "--config={}".format(config),
                        "lsjson", "-R",
                        "'{}'/'{}'/".format(source, job.show)])
        episode_list = loads(response.stdout.decode('utf-8'))
        for episode in episode_list:
            Ayumi.debug("Checking {} against episode {}".format(job.episode, episode['Name']))
            if episode['Name'] == job.episode:
                Ayumi.info("Found episode {} in {}".format(job.episode, source))
                return True
        Ayumi.info("Didn't find episode {} in {}".format(job.episode, source))
        return False
    except:
        # Typically hit if the source doesn't exist.
        Ayumi.warning("Error occured while checking source {} - does it exist?".format(source))
        return False

def download(job: Job, sources: List[str], tempfolder: str, config: str, flags: str) -> str:
    """
    Download the provided episode from sources
    Returns the path of the downloaded file
    job: Job to do!
    sources: list of rclone sources (EncoderConf.downloading_sources)
    tmppath: Path of the temporary folder
    rclone_config: Path to the rclone config file
    flags: rclone flags
    """
    for source in sources:
        Ayumi.debug("Checking for existence from source: {}".format(source))
        if _check_exists(config, source, job):
            Ayumi.info("Now downloading episode from source: {}".format(source))

            src_file = "'{}'/'{}'/'{}'".format(_clean(source), job.show, job.episode)
            Ayumi.debug("Sourcing from rclone path: {}".format(src_file))
            dest_file = "'{}'/'{}'".format(_clean(tempfolder), "temp")
            Ayumi.debug("Downloading to destination: {}".format(dest_file))


            command = ["rclone", "--config={}".format(config), "copyto", src_file, dest_file]
            command.extend(flags.split())

            Ayumi.debug("Now running command: {}".format(" ".join(command)))
            Ayumi.info("Now starting download.", color=Ayumi.LCYAN)

            try:
                _run(command)
            except ShikyouResponseException:
                Ayumi.error("Rclone command returned a bad return code, contact the developer.", color=Ayumi.LRED)
                raise ShikyouResponseException()
            except ShikyouTimeoutException:
                Ayumi.error("Rclone command timed out, are your sources okay?", color=Ayumi.LRED)
                raise ShikyouTimeoutException()

            Ayumi.info("Completed downloading files.", color=Ayumi.LGREEN)
            return dest_file
        else:
            Ayumi.debug("Requested episode doesn't exist under source {}".format(source))

    Ayumi.warning("No download sources contained the file.")
    return None

def upload(job: Job, destinations: List[str], upload_file: str, config: str, flags: str) -> None:
    """
    Upload the completed new hardsub file into the rclone destinations
    Returns a boolean based on success
    job: Job to do! This is the job of the HARDSUB file
    destinations: list of rlcone destinations (e.g., EncoderConf.uploading_destinations)
    upload_file: Path to the file to be uploaded
    rclone_config: Path to the rclone config file
    flags: rclone flag
    This method will upload the file and include its show name:
    e.g., 'temp.mp4' --> destination/show/episode.mp4
    """

    for dest in destinations:

        rclone_dest = "'{}'/'{}'/'{}'".format(_clean(dest), job.show, job.episode)
        command = ["rclone", "--config={}".format(config), "copyto", upload_file, rclone_dest]
        command.extend(flags.split())

        Ayumi.debug("Now running command: {}".format(" ".join(command)))
        Ayumi.info("Now uploading file to {}".format(dest))

        try:
            _run(command)
        except ShikyouResponseException:
            Ayumi.error("Rclone command returned a bad return code, contact the developer.", color=Ayumi.LRED)
            raise ShikyouResponseException()
        except ShikyouTimeoutException:
            Ayumi.error("Rclone command timed out, are your sources okay?", color=Ayumi.LRED)
            raise ShikyouTimeoutException()

    Ayumi.info("Completed uploading files.", color=Ayumi.LGREEN)