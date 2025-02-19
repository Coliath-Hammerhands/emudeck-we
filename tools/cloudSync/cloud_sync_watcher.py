# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "watchdog",
# ]
# ///
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import sys


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


print(sys.argv)
rclone_path = sys.argv[2]  # r"E:\Emulation\tools\rclone/rclone.exe"
rclone_cloud_drive = sys.argv[3]  # "Emudeck-OneDrive"
cloud_start_path = sys.argv[4]  # "Emudeck/saves"
save_path = sys.argv[5]  # "E:/Emulation/saves"
last_synced_time = {}


def run_command(command, recursion):
    time.sleep(1)
    if recursion > 2:
        return None

    try:
        subprocess.run(command, check=True)
        time.sleep(5)
    except subprocess.CalledProcessError as e:
        print(
            f"{bcolors.FAIL}WARNING: Command failed with return code {e.returncode}{bcolors.ENDC}"
        )
        run_command(command, recursion + 1)


def run_rclone_sync(path, call_time):
    global last_synced_time
    if path in last_synced_time:
        if (call_time - last_synced_time[path]) < 1:
            print(f"{bcolors.OKBLUE}skipped: ", path, bcolors.ENDC)
            return None
        else:
            last_synced_time[path] = call_time
    else:
        last_synced_time[path] = call_time
    rel_target = path.replace(save_path, cloud_start_path)
    print(f"{bcolors.OKGREEN}{rclone_cloud_drive}:{rel_target}{bcolors.ENDC}")
    # run_str = f"""rclone copy -v  --fast-list --update --tpslimit 12  --checkers=50 --exclude=/.fail_upload  --exclude=/.lock  --exclude=.lock --exclude=/BigPEmuConfig.bigpcfg --exclude=/.fail_download  --exclude=/system/prod.keys --exclude=/system/title.keys --exclude=/.pending_upload --exclude=/.watching  --exclude=/*.lnk --exclude=/.cloud --exclude=/.emulator --exclude=/.user "{path}" "{rclone_cloud_drive}:{rel_target}" """
    # run_command(run_str, 0)


class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        time.sleep(1)
        print(f"File created: {event.src_path}")
        if os.path.isfile(event.src_path):
            update_path = os.path.dirname(event.src_path)
            current_time = os.path.getmtime(event.src_path)
        elif os.path.isdir(event.src_path):
            update_path = event.src_path
            current_time = os.path.getmtime(event.src_path)
        else:
            print(
                f"{bcolors.OKCYAN}{bcolors.UNDERLINE}Hallucinated file {event.src_path}?{bcolors.ENDC}"
            )
            return None
        run_rclone_sync(update_path, current_time)

    def on_deleted(self, event):
        print(
            f"File deleted: {event.src_path}.{bcolors.BOLD}{bcolors.WARNING} You will have to manually remove it on the cloud side.{bcolors.ENDC}"
        )

    def on_modified(self, event):
        print(f"File modified: {event.src_path}")
        if os.path.isfile(event.src_path):
            update_path = os.path.dirname(event.src_path)
            current_time = os.path.getmtime(event.src_path)
        elif os.path.isdir(event.src_path):
            update_path = event.src_path
            current_time = os.path.getmtime(event.src_path)
        else:
            print(
                f"{bcolors.OKCYAN}{bcolors.UNDERLINE}Hallucinated file {event.src_path}?{bcolors.ENDC}"
            )
            return None
        run_rclone_sync(update_path, current_time)

    def on_moved(self, event):
        print(f"File moved from {event.src_path} to {event.dest_path}")
        if os.path.isfile(event.src_path):
            update_path = os.path.dirname(event.src_path)
            current_time = os.path.getmtime(event.src_path)
        elif os.path.isdir(event.src_path):
            update_path = event.src_path
            current_time = os.path.getmtime(event.src_path)
        else:
            print(
                f"{bcolors.OKCYAN}{bcolors.UNDERLINE}Hallucinated file {event.src_path}?{bcolors.ENDC}"
            )
            return None
        run_rclone_sync(update_path, current_time)


def main():
    # Specify the directory to monitor

    # Create a file system watcher
    observer = Observer()
    handler = MyHandler()

    # Start monitoring the directory
    observer.schedule(handler, save_path, recursive=True)

    # Start the event loop
    observer.start()
    watching = True
    try:
        while watching:
            time.sleep(1)
            if ".watching" not in os.listdir(save_path):
                watching = False
            # else:
            #     print(".")
        print(
            f"{bcolors.OKGREEN}{bcolors.UNDERLINE}{bcolors.BOLD}all done{bcolors.ENDC}"
        )
        time.sleep(5)
        observer.stop()
        exit()
    except KeyboardInterrupt:
        observer.stop()
    finally:
        observer.join()


if __name__ == "__main__":
    main()
