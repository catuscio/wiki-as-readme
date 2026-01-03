"""src.models.wiki_schema
Pydantic models for wiki structure, pages, sections, and repository structure.
"""

from typing import Annotated, Literal

from pydantic import BaseModel, Field


class WikiSection(BaseModel):
    id: Annotated[
        str,
        Field(
            description='Unique identifier for the section (e.g., "section-overview")'
        ),
    ]
    title: Annotated[str, Field(description='Title of the section (e.g., "Overview")')]
    pages: Annotated[
        list[str],
        Field(description="List of WikiPage IDs that belong directly to this section"),
    ]
    subsections: Annotated[
        list[str] | None,
        Field(description="List of WikiSection IDs that are children of this section"),
    ] = None


class WikiPage(BaseModel):
    id: Annotated[
        str,
        Field(
            description='Unique identifier for the page (e.g., "page-getting-started")'
        ),
    ]
    title: Annotated[
        str, Field(description='Title of the page (e.g., "Getting Started")')
    ]
    content: Annotated[
        str, Field(description="Leave this field empty. It will be generated later.")
    ]
    file_paths: Annotated[
        list[str],
        Field(
            description="List of relevant file paths from the repository for this page. Must contain at least 1 relevant file path."
        ),
    ]
    importance: Annotated[
        Literal["high", "medium", "low"], Field(description="Importance of the page")
    ]
    related_pages: Annotated[
        list[str],
        Field(description="List of WikiPage IDs that are related to this page"),
    ]
    parent_id: Annotated[
        str | None,
        Field(
            description="ID of the parent section this page belongs to. Can be null if it's a top-level page."
        ),
    ] = None


class WikiStructure(BaseModel):
    id: Annotated[
        str,
        Field(
            description='Overall unique identifier for the wiki (e.g., "repository-wiki")'
        ),
    ]
    title: Annotated[
        str, Field(description='Overall title for the wiki (e.g., "My Project Wiki")')
    ]
    description: Annotated[
        str, Field(description="Brief description of the entire wiki/repository")
    ]

    pages: Annotated[
        list[WikiPage], Field(description="List of all WikiPage objects in the wiki")
    ]
    sections: Annotated[
        list[WikiSection],
        Field(
            description="List of all WikiSection objects in the wiki. Must be provided, even as an empty list."
        ),
    ]
    root_sections: Annotated[
        list[str],
        Field(description="List of WikiSection IDs that are top-level sections."),
    ]


class RepositoryStructure(BaseModel):
    """Internal model to hold repository structure information."""

    file_tree: str
    readme: str
    default_branch: str = "main"
    error: str | None = None
