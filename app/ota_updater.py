import requests
from app.lib.tarfile import TarFile, DIRTYPE
import os


class OTAUpdater:
    def __init__(
        self,
        github_repo,
        app_dir="app",
        new_version_dir="next",
        current_version="v0.0.0",
    ):
        self.github_repo = github_repo.rstrip("/")
        self.app_dir = app_dir
        self.new_version_dir = new_version_dir
        self.current_version = current_version
        self.latest_version = "v0.0.0"

    def check_and_download(self):
        latest_release = self.get_latest_release()
        self.latest_version = self.get_latest_version(latest_release)
        if self.compare_versions():
            self.download_release(latest_release)
            return True

        return False

    def apply_update(self):
        if self._exists_dir(self.new_version_dir) and "version.txt" in os.listdir(
            self.new_version_dir
        ):
            latest_version = "v0.0.0"
            with open(self.new_version_dir + "/version.txt", "r") as f:
                latest_version = f.readline()
                f.close()

            print(f"Found new version: {latest_version}")
            self.rmtree(self.app_dir)
            os.remove("version.txt")
            os.remove("main.py")

            os.rename(self.new_version_dir + "/" + self.app_dir, self.app_dir)
            os.rename(self.new_version_dir + "/version.txt", "version.txt")
            os.rename(self.new_version_dir + "/main.py", "main.py")

            self.rmtree(self.new_version_dir)

            print("OTA update applied succesfully!")
            return True

        return False

    def download_release(self, latest_release):
        assets = latest_release.get("assets", [])
        if not len(assets):
            print("No assets to download")
            return

        tar_url = assets[0].get("browser_download_url")
        if not tar_url:
            print("No tar_url to donwload")
            return

        asset_filename = (
            self.new_version_dir
            + "/"
            + self.get_latest_version(latest_release)
            + ".tar"
        )

        if self._exists_dir(self.new_version_dir):
            self.rmtree(self.new_version_dir)

        self.mkdir(self.new_version_dir)

        try:
            print(f'Downloading "{tar_url}"...')
            resp = requests.get(tar_url, headers={"User-Agent": "MicroPython Client"})

            CHUNK_SIZE = 512  # bytes
            with open(asset_filename, "w") as outfile:
                data = resp.raw.read(CHUNK_SIZE)
                while data:
                    outfile.write(data)
                    data = resp.raw.read(CHUNK_SIZE)
                outfile.close()

            resp.raw.close()
            print(f'Downloaded successfully "{asset_filename}"')

            t = TarFile(asset_filename)
            for i in t:
                path = self.new_version_dir + "/" + i.name
                print(f"Extracting '{path}'")
                if i.type == DIRTYPE:
                    self.mkdir(path[:-1])
                else:
                    f = t.extractfile(i)
                    with open(path, "wb") as of:
                        of.write(f.read())
                        of.close()

            os.remove(asset_filename)

            with open(self.new_version_dir + "/version.txt", "w") as file:
                file.write(self.get_latest_version(latest_release))
                file.close()

        except Exception as e:
            print(e)

    def compare_versions(self):
        latest_version = self.latest_version
        current_version = self.current_version
        if self.latest_version.startswith("v"):
            latest_version = self.latest_version[1:]

        if self.current_version.startswith("v"):
            current_version = self.current_version[1:]

        print(
            "currentVersion: %s, latestVersion: %s" % (current_version, latest_version)
        )

        return self._version_as_tuple(latest_version) > self._version_as_tuple(
            current_version
        )

    def get_latest_version(self, latest_release):
        latest_version = "v0.0.0"

        if latest_release:
            latest_version: str = latest_release.get("tag_name", "v0.0.0")

        return latest_version

    def get_latest_release(self):
        print("Fetching latest release...")
        latest_release = requests.get(
            f"https://api.github.com/repos/{self.github_repo}/releases/latest",
            headers={"User-Agent": "MicroPython Client"},
        )

        try:
            if latest_release.status_code == 200:
                latest_release = latest_release.json()
                return latest_release
        except Exception as e:
            print("Exception", e)
        return None

    def mkdir(self, path: str):
        try:
            os.mkdir(path)
        except OSError as exc:
            if exc.args[0] == 17:
                pass

    def _version_as_tuple(self, v: str):
        return tuple(map(int, (v.split("."))))

    def _exists_dir(self, path) -> bool:
        try:
            os.listdir(path)
            return True
        except:
            return False

    def rmtree(self, d):
        if not d:
            raise ValueError

        for name, type, *_ in os.ilistdir(d):
            path = d + "/" + name
            if type & 0x4000:  # dir
                self.rmtree(path)
            else:  # file
                os.unlink(path)
        os.rmdir(d)
