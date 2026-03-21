import os

def deliver_home_view() -> str:
    """
    Reads the HTML view file and returns it.
    Follows MVC: Controller fetching from View.
    """
    view_path = os.path.join(os.path.dirname(__file__), "..", "views", "index.html")
    
    try:
        with open(view_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        return f"<h1>Error loading view: {str(e)}</h1>"
