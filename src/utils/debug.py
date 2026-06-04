from chatbot_wpp2.src.database.db import fetchall

def print_table(
        table_name: str, 
        columns: list = None, 
        where: str = None, 
        params: tuple = (),
        limit: int = None,
        max_width: int = 80
        ):
    """
    Imprime tabela com tratamento para campos longos (como JSON).
    """
    
    col_str = ", ".join(columns) if columns else "*"
    query = f"SELECT {col_str} FROM {table_name}"
    
    if where:
        query += f" WHERE {where}"
    if limit:
        query += f" LIMIT {limit}"
    
    rows = fetchall(query, params)
    
    if not rows:
        print(f"Tabela '{table_name}' está vazia.\n")
        return
    
    # Nomes das colunas
    col_names = columns if columns else list(rows[0].keys())
    
    # Calcula largura máxima por coluna (com limite)
    col_widths = {col: len(col) for col in col_names}
    
    for row in rows:
        for col in col_names:
            value = str(row[col])
            
            # Tratamento especial para campos muito grandes (ex: JSON)
            if len(value) > max_width:
                value = value[:max_width-3] + "..."
            
            col_widths[col] = max(col_widths[col], len(value))
    
    # Limita a largura máxima de cada coluna
    for col in col_names:
        col_widths[col] = min(col_widths[col], max_width)
    
    # Cabeçalho
    header = " | ".join(col.ljust(col_widths[col]) for col in col_names)
    separator = "-+-".join("-" * col_widths[col] for col in col_names)
    
    print(f"Tabela: {table_name.upper()}\n")
    print(f"{header}\n")
    print(f"{separator}\n")
    
    # Linhas
    for row in rows:
        line_parts = []
        for col in col_names:
            value = str(row[col])
            
            # Trunca JSONs e textos longos
            if len(value) > max_width:
                value = value[:max_width-3] + "..."
            
            line_parts.append(str(value).ljust(col_widths[col]))
        
        print(" | ".join(line_parts))
    
    print(f"Total de registros: {len(rows)}\n")