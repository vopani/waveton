from h2o_wave import ui


def get_inline_script(text: str) -> ui.InlineScript:
    """
    Get Wave's Inline Script.
    """

    return ui.inline_script(text)
