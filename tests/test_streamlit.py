from pathlib import Path
from streamlit.testing.v1 import AppTest

def test_original_streamlit_launch_and_local_demo():
    app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'rag_streamlit.py')).run(timeout=30)
    assert not app.exception
    next(button for button in app.button if button.label=='Load synthetic demo').click().run(timeout=30)
    assert not app.exception and len(app.dataframe)==1
    assert len(app.dataframe[0].value)==27
