import os
from typing import List, Optional

import yaml
from pydantic import BaseModel, Field

from cli.util import is_git_repo, get_git_root

DEFAULT_FILE_PATH = ".pilot-skills.yaml"


class AgentSkill(BaseModel):
    """User-defined skill for the PR Pilot agent."""

    title: str = Field(..., title="Short title of the skill")
    args: Optional[dict] = Field(None, title="Arguments required to perform the skill")
    instructions: str = Field(..., title="Instructions for the agent")
    result: Optional[str] = Field(
        "A short summary of your actions", title="Expected result of the skill"
    )


def find_pilot_skills_file() -> Optional[str]:
    """Discover the location of the .pilot-skills.yaml file.

    The file is searched for in the following order:
    1. The root of the current Git repository
    2. The home directory

    :return: The absolute path to the file, or None if not found.
    """
    # Check if the current directory is part of a Git repository
    if is_git_repo():
        git_root = get_git_root()
        if git_root:
            git_repo_file_path = os.path.join(git_root, ".pilot-skills.yaml")
            if os.path.isfile(git_repo_file_path):
                return os.path.abspath(git_repo_file_path)
            else:
                # Create the file if it doesn't exist
                with open(git_repo_file_path, "w") as file:
                    file.write("skills: []")
    else:
        return None

    # If not found in the Git repository, check the home directory
    home_file_path = os.path.expanduser("~/.pilot-skills.yaml")
    if os.path.isfile(home_file_path):
        return os.path.abspath(home_file_path)

    # If the file is not found in either location, return None
    return None


class SkillIndex:
    """
    A class to manage the index of skills stored in a YAML file.
    """

    def __init__(self, file_path: str = None):
        """
        Initialize the SkillIndex with the given file path.

        :param file_path: Path to the YAML file containing skills.
        """
        self.file_path = file_path
        if not self.file_path:
            self.file_path = find_pilot_skills_file()
        self.skills = self._load_skills()

    def _load_skills(self) -> List[dict]:
        """
        Load skills from the YAML file.

        :return: A list of skill dictionaries.
        """
        try:
            with open(self.file_path, "r") as file:
                data = yaml.safe_load(file)
                return data.get("skills", [])
        except FileNotFoundError:
            return []

    def save_skills(self) -> None:
        """
        Save the current list of skills to the YAML file.
        """
        with open(self.file_path, "w") as file:
            yaml.dump(
                {"skills": self.skills},
                file,
            )

    def add_skill(self, new_skill: dict) -> None:
        """
        Add a new skill to the list and save it.

        :param new_skill: The skill dictionary to add.

        :raises ValueError: If a skill with the same name already exists.
        """
        for skill in self.skills:
            if skill.get("name") == new_skill.get("name"):
                raise ValueError(f"Skill with name '{new_skill.get('name')}' already exists")
        self.skills.append(new_skill)
        self.save_skills()

    def get_skills(self) -> List[dict]:
        """
        Get the list of skills.

        :return: A list of skill dictionaries.
        """
        return self.skills

    def get_skill(self, skill_name: str) -> Optional[dict]:
        """
        Get a skill by name.

        :param skill_name: The name of the skill.
        :return: The skill dictionary, or None if not found.
        """
        for skill in self.skills:
            if skill.get("name") == skill_name:
                return skill
        return None

    def remove_skill(self, skill_name: str) -> None:
        """
        Remove a skill by name.

        :param skill_name: The name of the skill to remove.
        """
        self.skills = [skill for skill in self.skills if skill.get("name") != skill_name]
        self.save_skills()
