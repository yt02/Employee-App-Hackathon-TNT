import os
import zipfile


def create_zip():
    # Keep deployment package minimal and deterministic for Oryx.
    exclude_dirs = {
        ".venv",
        "venv",
        "antenv",
        "packages",
        "__pycache__",
        ".azure",
        ".git",
        ".pytest_cache",
        ".mypy_cache",
        "tmp_inspect",
        "tmp_inspect_v2",
        "azure_logs",
        "webapp_logs",
        "logs",
        "latest_logs",
        "temp_deploy",
        "test_deploy",
        "test_deploy_v2",
        "test_deploy_v3",
    }
    exclude_files = {"deploy.zip", "build_zip.py", ".gitignore", ".env", "app_settings.json"}

    with zipfile.ZipFile("deploy.zip", "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk("."):
            # Prune exclude directories and any starting with . or tmp_
            dirs[:] = [
                d
                for d in dirs
                if d not in exclude_dirs and not d.startswith(".") and not d.startswith("tmp_")
            ]

            for file in files:
                if file in exclude_files or file.endswith((".pyc", ".zip", ".log")):
                    continue

                file_path = os.path.join(root, file)
                # Strip leading './' or '.\\'
                rel_path = os.path.relpath(file_path, ".")
                # Ensure forward slashes for Linux compatibility
                arcname = rel_path.replace(os.sep, "/")

                print(f"Adding: {arcname}")
                zf.write(file_path, arcname=arcname)

    print("\nCreated deploy.zip successfully.")


if __name__ == "__main__":
    create_zip()