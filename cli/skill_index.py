import os
from typing import List, Optional

import yaml
from pydantic import BaseModel, Field

from cli.util import is_git_repo, get_git_root

SKILL_FILE_PATH = ".pilot-skills.yaml"


def str_presenter(dumper, data):
    if "\n" in data:  # Check if the string contains newlines
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


# Add the custom representer to handle multiline strings
yaml.add_representer(str, str_presenter)


class AgentSkill(BaseModel):
    """User-defined skill for the PR Pilot agent."""

    title: str = Field(..., title="Short title of the skill")
    args: Optional[dict] = Field(None, title="Arguments required to perform the skill")
    instructions: str = Field(..., title="Instructions for the agent")
    result: Optional[str] = Field(
        "A short summary of your actions", title="Expected result of the skill"
    )

    def dict(self, *args, **kwargs):
        original_dict = super().dict(*args, **kwargs)
        # Reorder the dictionary as desired
        ordered_dict = {
            "title": original_dict["title"],
            "args": original_dict["args"],
            "instructions": original_dict["instructions"],
            "result": original_dict["result"],
        }
        return ordered_dict


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
            git_repo_file_path = os.path.join(git_root, SKILL_FILE_PATH)
            if os.path.isfile(git_repo_file_path):
                return os.path.abspath(git_repo_file_path)
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

        self.skills = self._load_skills() if self.file_path else []

    def _load_skills(self) -> List[AgentSkill]:
        """
        Load skills from the YAML file.

        :return: A list of AgentSkill objects.
        """
        try:
            with open(self.file_path, "r") as file:
                data = yaml.safe_load(file)
                return [AgentSkill(**skill) for skill in data]
        except FileNotFoundError:
            return []

    def save_skills(self) -> None:
        """
        Save the current list of skills to the YAML file.
        """
        with open(self.file_path, "w") as file:
            yaml.dump(
                [skill.dict() for skill in self.skills],
                file,
                default_flow_style=False,
                allow_unicode=True,
            )

    def add_skill(self, new_skill: AgentSkill) -> None:
        """
        Add a new skill to the list and save it.

        :param new_skill: The AgentSkill object to add.

        :raises ValueError: If a skill with the same name already exists.
        """
        for skill in self.skills:
            if skill.title == new_skill.title:
                raise ValueError(f"Skill with title '{new_skill.title}' already exists")
        self.skills.append(new_skill)
        self.save_skills()

    def get_skills(self) -> List[AgentSkill]:
        """
        Get the list of skills.

        :return: A list of AgentSkill objects.
        """
        return self.skills

    def get_skill(self, skill_title: str) -> Optional[AgentSkill]:
        """
        Get a skill by title.

        :param skill_title: The title of the skill.
        :return: The AgentSkill object, or None if not found.
        """
        for skill in self.skills:
            if skill.title == skill_title:
                return skill
        return None

    def remove_skill(self, skill_title: str) -> None:
        """
        Remove a skill by title.

        :param skill_title: The title of the skill to remove.
        """
        self.skills = [skill for skill in self.skills if skill.title != skill_title]
        self.save_skills()
