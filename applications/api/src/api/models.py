from jats_classes import Front
from pydantic import BaseModel, Field

# HTTP Error Responses


# 400 Bad Request
class HTTP400BadRequest(BaseModel):
    detail: str = Field(default="Bad request.", examples=["Bad request."])


# 404 Not Found
class HTTP404NotFound(BaseModel):
    detail: str = Field(
        default="The requested resource was not found.", examples=["The requested resource was not found."]
    )


# 413 Payload Too Large
class HTTP413PayloadTooLarge(BaseModel):
    detail: str = Field(default="The uploaded file is too large.", examples=["The uploaded file is too large."])


# 415 Unsupported Media Type
class HTTP415UnsupportedMediaType(BaseModel):
    detail: str = Field(default="Unsupported media type.", examples=["Unsupported media type."])


# 500 Internal Server Error
class HTTP500InternalServerError(BaseModel):
    detail: str = Field(default="An unexpected error occurred.", examples=["An unexpected error occurred."])


# 200 Responses


class UploadFileResponse(BaseModel):
    urls: list[str] = Field(
        description="The URLs of the uploaded files",
        examples=[["http://example.com/files/uploaded_file1", "http://example.com/files/uploaded_file2"]],
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


class CacheStatusResponse(BaseModel):
    enabled: bool = Field(description="Indicates if FastAPICache is enabled")
    prefix: str = Field(description="The cache prefix used by FastAPICache")


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
