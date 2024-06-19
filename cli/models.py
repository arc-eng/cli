from pydantic import BaseModel, Field
from typing import Optional


class TaskParameters(BaseModel):
    """
    Model representing the parameters for a task.
    """

    wait: bool = Field(default=False, description="Wait for the task to complete")
    repo: Optional[str] = Field(default=None, description="Repository to run the task on")
    snap: bool = Field(default=False, description="Take a screenshot")
    verbose: bool = Field(default=False, description="Print more status messages")
    cheap: bool = Field(default=False, description="Use the cheap model")
    code: bool = Field(default=False, description="Include code primer")
    file: Optional[str] = Field(default=None, description="File to use for the prompt template")
    direct: bool = Field(default=False, description="Directly output the prompt")
    output: Optional[str] = Field(default=None, description="Output file for the prompt")
    model: Optional[str] = Field(default=None, description="Model to use for the task")
    debug: bool = Field(default=False, description="Run in debug mode")
    prompt: Optional[str] = Field(default=None, description="Prompt to use for the task")
    branch: Optional[str] = Field(default=None, description="Branch to use for the task")
    pr_number: Optional[int] = Field(default=None, description="Pull request number")
    spinner: bool = Field(default=True, description="Display spinners")
    sync: bool = Field(
        default=False, description="Sync local repository state with PR Pilot changes"
    )
