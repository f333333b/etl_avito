def save_to_excel(df, path: str):
    df = df.copy()
    for col in df.select_dtypes(include=["datetimetz"]).columns:
        df[col] = df[col].dt.tz_localize(None)
    df.to_excel(path, index=False)