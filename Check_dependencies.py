import subprocess
from model_package.path_module import REQUIREMENTS_FILE_PATH
import importlib as imp


def check_dependencies():
    # Read the list of required packages and versions from requirements.txt
    with open(REQUIREMENTS_FILE_PATH, 'r') as f:
        required_packages = [line.strip()
                             for line in f.readlines() if line.strip()]

    # Check if each required package is installed with the correct version
    missing_packages = []
    for requirement in required_packages:
        parts = requirement.split('>=')
        package = parts[0]
        version = None if len(parts) == 1 else parts[1]
        try:
            module = imp.import_module(package)
            installed_version = getattr(module, '__version__', None)

            if version and installed_version and installed_version >= version:
                print(f"{package} är installerad och version: {installed_version}")

            elif not version:
                print(
                    f"{package} installerat och är versionsoberoende, version: {installed_version}")

            else:
                print(
                    f"{package} is är installerat med lägre version med oklar kompabilitet.")
        except ImportError:
            print(f"{package} är inte installerad.")
            missing_packages.append(requirement)

    # If there are missing packages, prompt the user to install them
    if missing_packages:
        print("\nFollowing paket saknas:")
        print("\n".join(missing_packages))
        answer = input("Önskar du att installera dess y = ja, n = nej? (y/n) ")
        if answer.lower() == "y":
            subprocess.call(["pip", "install", "--upgrade"] + missing_packages)
            print("Paket har framgångsrikt installerats!")
        else:
            print("Du har valt att inte installera nödvändiga paket, avslutar RSS-MATIX.")
            exit()
    else:
        print("Alla nödvändiga paket är redan installerade!")


if __name__ == "__main__":
  # Test
    check_dependencies()
