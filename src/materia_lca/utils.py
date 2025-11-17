

def handle_produit_type(text: str):
    # split into left (classification) / right (process name)
    if "-" in text:
        left, right = text.split("-", 1)
    process_name = right.strip()
    parts = [p.strip() for p in left.split("/") if p.strip()]
    return parts, process_name


def UUID_finder(process_name, df_ref) -> str:   # call this function after add_process, right structure ?
    column = df_ref["Produits (nouvelle dénomination)"].astype(str).str.strip() # gets rid of whitespaces in cells of column
    match_row = df_ref.loc[column == process_name].iloc[0] #returns first matching row
    return str(match_row["Identifiant UUID"])