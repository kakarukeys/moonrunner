import argparse
import os
import re
import subprocess
import shutil

import jinja2
import requests


env = jinja2.Environment(loader=jinja2.FileSystemLoader("d:\\"))

# parse arguments
parser = argparse.ArgumentParser(description="Moonrunner - the great project boostrapper")
parser.add_argument(
    "action", 
    choices=("new", "load", "delete"), 
    metavar="action", 
    help="new / load / delete"
)
parser.add_argument(
    "-n", "--name",
    help="the project and virtual environment name"
)
parser.add_argument(
    "-r", "--repo", 
    help="the repository url to clone the project"
)
parser.add_argument(
    "-t", "--type", 
    choices=("django", "angular"),
    metavar="TYPE",
    help="special project type: django/angular (not passed = no special type)"
)
parser.add_argument(
    "-v", "--ver", 
    default=26, 
    choices=(26, 27, 33), 
    type=int,
    metavar="VER",
    help="the Python verison: 26/27/33"
)
args = parser.parse_args()

# test for argument errors and process arguments
if args.action in ("new", "delete") and args.name is None:
    parser.error("-n is required by " + args.action)
if args.action == "load" and args.repo is None:
    parser.error("-r is required by " + args.action)
    
if args.action == "new" and requests.get("https://github.com/kakarukeys/" + args.name).status_code == 200:
    raise Exception("Project {0} already existed on GitHub".format(args.name))
elif args.action == "load":
    m = re.search(r"git@github\.com:(.+?)/(.+?)\.git", args.repo)
    https_url = "https://github.com/{0}/{1}".format(m.group(1), m.group(2))
    print("testing for https URL: " + https_url)
    if requests.get(https_url).status_code != 200:
        raise Exception("Repository {0} does not exist on GitHub".format(args.repo))
    else:
        print("Using {0} as name", m.group(2))
        args.name = m.group(2)
        
project_dir = os.path.join("d:", "projects", args.name)
ve_dir = os.path.join("d:", "virtualenvs", args.name)

if args.action in ("new", "load"):
    print("Creating project directory...")
    if os.path.exists(project_dir):
        raise Exception("Project directory {0} already existed!".format(project_dir))
    elif os.path.exists(ve_dir):
        raise Exception("Virtual environment directory {0} already existed!".format(ve_dir))
    else:
        os.makedirs(project_dir)
        
    print("Executing shell commands...")
    template = env.get_template("{0}_repo.sh.jinja2".format(args.action))
    with open(r"d:\{0}_repo.sh".format(args.action), 'w') as f:
        f.write(template.render(**args.__dict__))
    subprocess.check_call((
        r"c:\Program Files\Git\bin\sh.exe", 
        "-x",
        r"d:\{0}_repo.sh".format(args.action)
    ))
    print("Success.")
    
elif args.action == "delete":
    print("delete project {0}? [y/N]".format(args.name))
    if input().lower() == 'y':
        subprocess.check_call((
            "rm", 
            "-rf",
            project_dir,
            ve_dir
        ))
        print("deleted {0} and {1}".format(project_dir, ve_dir))
        
else:
    raise Exception("unknown action")
