from textual import events
from textual.widgets import DataTable

class StretchyDataTable(DataTable):
    def on_resize(self, event: events.Resize) -> None:
        total_width = event.size.width
        if len(self.columns) == 0:
            return
        
        total_padding = 2 * (self.cell_padding * len(self.columns))
        column_width = (total_width - total_padding) // len(self.columns)

        for column in self.columns.values():
            column.auto_width = False
            column.width = column_width
        
        self.refresh()
