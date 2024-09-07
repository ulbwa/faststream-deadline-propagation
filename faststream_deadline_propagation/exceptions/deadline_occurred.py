class DeadlineOccurred(Exception):
    def __init__(self):
        super().__init__("The deadline has occurred.")


__all__ = ("DeadlineOccurred",)
