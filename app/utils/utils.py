import pandas as pd
import base64
import io

def parse_contents(contents):
    if contents is None:
        return None

    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

    return df