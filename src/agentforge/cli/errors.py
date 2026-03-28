class PipelineError(Exception):
    """Base exception for pipeline errors"""

    def __init__(self, stage: str, message: str, hint: str = ""):
        self.stage = stage
        self.hint = hint
        super().__init__(message)


class SearchAPIError(PipelineError):
    """Raised when search API fails"""

    def __init__(self, message: str):
        super().__init__(
            stage="search",
            message=message,
            hint="Set TAVILY_API_KEY or use --no-search to skip",
        )


class GenerationError(PipelineError):
    """Raised when file generation fails"""

    def __init__(self, message: str):
        super().__init__(
            stage="generation",
            message=message,
            hint="Check output directory permissions",
        )


class CompressionError(PipelineError):
    """Raised when compression fails"""

    def __init__(self, message: str):
        super().__init__(
            stage="compression", message=message, hint="Check input data format"
        )


class IntentParseError(PipelineError):
    """Raised when intent parsing fails"""

    def __init__(self, message: str):
        super().__init__(
            stage="intent_parsing", message=message, hint="Check the prompt format"
        )
