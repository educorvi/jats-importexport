from jats_classes import Front
from pydantic import BaseModel, Field, RootModel

# HTTP Error Responses


# 400 Bad Request
class HTTP400BadRequest(BaseModel):
    detail: str = Field(default="Bad request.", examples=["Bad request."])


# 404 Not Found
class HTTP404NotFound(BaseModel):
    detail: str = Field(
        default="The requested resource was not found.", examples=["The requested resource was not found."]
    )


class HTTP409Conflict(BaseModel):
    detail: str = Field(default="Conflict.", examples=["Conflict occurred."])


# 413 Payload Too Large
class HTTP413PayloadTooLarge(BaseModel):
    detail: str = Field(default="The uploaded file is too large.", examples=["The uploaded file is too large."])


# 415 Unsupported Media Type
class HTTP415UnsupportedMediaType(BaseModel):
    detail: str = Field(default="Unsupported media type.", examples=["Unsupported media type."])


# 422 Unprocessable Entity
class HTTP422UnprocessableEntity(BaseModel):
    detail: str = Field(default="Unprocessable entity.", examples=["Unprocessable content."])


# 500 Internal Server Error
class HTTP500InternalServerError(BaseModel):
    detail: str = Field(default="An unexpected error occurred.", examples=["An unexpected error occurred."])


# 200 Responses


class UploadFileResponse(BaseModel):
    urls: list[str] = Field(
        description="The URLs of the uploaded files",
        examples=[["http://example.com/files/uploaded_file1", "http://example.com/files/uploaded_file2"]],
    )


class UpdateArticlesResponse(BaseModel):
    updated_articles: list[str] = Field(
        description="The list of updated article paths (relative to the storage base URL)",
        examples=[["articles/article1.xml", "articles/article2.xml"]],
    )


class DeleteArticleResponse(BaseModel):
    detail: str = Field(
        default=(
            "Errors occurred during the deletion of the referenced assets."
            " The article was successfully deleted but some associated files could not be removed."
            " Check the errors list for details."
        ),
        examples=[
            (
                "Errors occurred during the deletion of the referenced assets."
                " The article was successfully deleted but some associated files could not be removed."
                " Check the errors list for details."
            )
        ],
    )
    errors: list[str] = Field(
        description="A list of errors encountered during the deletion process",
        examples=[["Error deleting image1.png", "Error deleting image2.png"]],
    )


class JatsDocumentResponse(BaseModel):
    jats: str = Field(description="The JATS XML document")


class HtmlDocumentResponse(BaseModel):
    html: str = Field(description="The HTML document (main content)")
    front: str = Field(description="The HTML of the front matter / metadata section")


class MarkdownDocumentResponse(BaseModel):
    md: str = Field(description="The Markdown document")


class MetadataResponse(BaseModel):
    metadata: Front = Field(description="The metadata")


class CacheClearedResponse(BaseModel):
    message: str = Field(description="Confirmation message for cache clearance")


class CacheStatus(BaseModel):
    implementation: str = Field(description="The cache implementation")
    items_in_cache: int = Field(description="The number of items currently in the cache")


class CacheStatusResponse(RootModel[dict[str, CacheStatus]]):
    pass


class ListBatching(BaseModel):
    current: str = Field(description="URL of the current batch")
    next: str | None = Field(description="URL of the next batch, if one exists")
    previous: str | None = Field(description="URL of the previous batch, if one exists")
    first: str = Field(description="URL of the first batch")
    last: str = Field(description="URL of the last batch")


class ListArticlesResponse(BaseModel):
    articles: list[str] = Field(description="The list of article paths (relative to the storage base URL)")
    count: int = Field(description="The total number of matching articles across all batches")
    batching: ListBatching = Field(description="Links for navigating between batches")


class ListFachbereicheResponse(BaseModel):
    fachbereiche: list[str] = Field(description="The list of Fachbereiche")


class ListSachgebieteResponse(BaseModel):
    sachgebiete: list[str] = Field(description="The list of Sachgebiete")


class AsyncExportAccepted(BaseModel):
    status: str = Field(description="The status of the export")
