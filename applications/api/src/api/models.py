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
    url: str = Field(description="The URL of the uploaded file", examples=["http://example.com/files/uploaded_file"])


class JatsDocumentResponse(BaseModel):
    jats: str = Field(description="The JATS XML document")


class HtmlDocumentResponse(BaseModel):
    html: str = Field(description="The HTML document")


class CacheClearedResponse(BaseModel):
    message: str = Field(description="Confirmation message for cache clearance")


class CacheStatusResponse(BaseModel):
    enabled: bool = Field(description="Indicates if FastAPICache is enabled")
    prefix: str = Field(description="The cache prefix used by FastAPICache")
