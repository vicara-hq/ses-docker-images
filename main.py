from urllib import request,parse
import subprocess
from bs4 import BeautifulSoup
import re
import json
import configparser
import logging

config = configparser.ConfigParser()
config.read("config.ini")

LOG_LEVEL = int(config["logging"]["debug"])
if LOG_LEVEL:
    logging.basicConfig(level=logging.DEBUG)

SES_BASE_URL = config["segger-studio"]["BaseURL"]
SES_DOCKER_REPO = config["segger-studio"]["DockerRepo"]

LIST_TAGS_URL = "https://registry.hub.docker.com/v1/repositories/{}/tags"

def run_shell_command(command):
    subprocess.run(command, shell=True)

def build_docker_image(name, download_url):
    logging.info("Building {}".format(name))
    run_shell_command("docker build --build-arg download_url=\"{}\" -t \"{}\" .".format(download_url, name))

def publish_docker_image(image):
    logging.info("Publishing {}".format(image))
    run_shell_command("docker push {}".format(image))

def delete_docker_image(image):
    logging.info("Deleting {}".format(image))
    run_shell_command("docker rmi -f {}".format(image))

def list_repo_tags(image):
    url = LIST_TAGS_URL.format(image)
    tags_obj = json.load(request.urlopen(url))
    logging.info("{} tags built in {} repo".format(len(tags_obj), image))
    return list(map(lambda tag:tag["name"], tags_obj))

def get_ses_downloads():
    downloads = dict()
    downloads_page = BeautifulSoup(request.urlopen(SES_BASE_URL), features="html.parser")

    latest = downloads_page.find("tr", class_="id_EmbeddedStudio_ARM_Linux_x64")
    latest_version = latest.find("div", class_= "dl_version", text=True).text.lstrip("V")
    downloads[latest_version] = "https://www.segger.com/downloads/embedded-studio/EmbeddedStudio_ARM_Linux_x64"

    for a in downloads_page.find_all("a", href=True):
        link = a["href"]
        match = re.search(r"Setup_EmbeddedStudio(_ARM)?_v([a-z0-9]+)_linux_x64.tar.gz$", link, re.IGNORECASE)
        if match:
            version = match.group(2).replace("_",".")
            download_link = link
            downloads[version] = download_link
                
    logging.info("Found {} versions of ses available".format(len(downloads)))
    return downloads

def main():
    ses_built_tags = list_repo_tags(SES_DOCKER_REPO)

    ses_downloads = get_ses_downloads()

    ses_build_tags = list(set(ses_downloads.keys()) - set(ses_built_tags))
    
    if len(ses_build_tags):
        logging.info("ses tags to build:\n{}".format(" ".join(ses_build_tags)))

    finished_builds = []

    for tag in ses_build_tags:
        build_tag = "{}:{}".format(SES_DOCKER_REPO, tag)
        build_docker_image(build_tag, ses_downloads[tag])
        publish_docker_image(build_tag)
        finished_builds.append(build_tag)
    
    map(delete_docker_image, finished_builds)

main()