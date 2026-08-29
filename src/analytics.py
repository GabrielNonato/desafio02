"""Comentario V1 - Indicadores, exportações e gráficos - gera estatísticas, exporta dados e cria visualizações dos atendimentos."""
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def build_indicators(df: pd.DataFrame) -> dict:
    # Comentario V1 - Constrói dicionário com indicadores estatísticos: contagens, médias, medianas e desvios padrão
    # Comentario V1 - Extrai coluna de tempo, converte para numérico removendo NaN
    times=pd.to_numeric(df.get("tempo_minutos"),errors="coerce").dropna().to_numpy(dtype=float)
    return {
      # Comentario V1 - Total de registros no DataFrame
      "total_registros":int(len(df)),
      # Comentario V1 - Agrupamento de registros por classificação (válido, inválido, incompleto, duplicado)
      "por_classificacao":df.get("classificacao",pd.Series(dtype=str)).value_counts(dropna=False).to_dict(),
      # Comentario V1 - Contagem de registros por categoria de atendimento
      "por_categoria":df.get("categoria",pd.Series(dtype=str)).value_counts(dropna=False).to_dict(),
      # Comentario V1 - Contagem de registros por status (Concluido, Pendente, Em atendimento)
      "por_status":df.get("status",pd.Series(dtype=str)).value_counts(dropna=False).to_dict(),
      # Comentario V1 - Cálculo da média de tempo de atendimento em minutos
      "tempo_medio":float(np.mean(times)) if times.size else None,
      # Comentario V1 - Cálculo da mediana de tempo de atendimento
      "tempo_mediano":float(np.median(times)) if times.size else None,
      # Comentario V1 - Cálculo do desvio padrão dos tempos (variação de tempo entre atendimentos)
      "tempo_desvio_padrao":float(np.std(times)) if times.size else None,
      # Comentario V1 - Percentual de registros processados via OCR em relação ao total
      "percentual_ocr":float((df.get("metodo",pd.Series(dtype=str))=="ocr").mean()*100) if len(df) else 0.0,
    }

def export_results(df: pd.DataFrame, output_dir: str | Path, csv_name: str, json_name: str) -> dict:
    # Comentario V1 - Exporta DataFrame em CSV e indicadores em JSON para diretório de saída
    # Comentario V1 - Cria diretório de saída se não existir
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    # Comentario V1 - Calcula indicadores a partir do DataFrame
    indicators=build_indicators(df)
    # Comentario V1 - Salva DataFrame em arquivo CSV sem índice de linha
    df.to_csv(out/csv_name,index=False,encoding="utf-8")
    # Comentario V1 - Salva indicadores em arquivo JSON com formatação e suporte a float
    (out/json_name).write_text(json.dumps(indicators,ensure_ascii=False,indent=2,default=float),encoding="utf-8")
    # Comentario V1 - Retorna dicionário de indicadores para log ou processamento adicional
    return indicators

def generate_charts(df: pd.DataFrame, directory: str | Path) -> None:
    # Comentario V1 - Gera gráficos de barras em PNG: categoria, status e tempo médio por categoria
    # Comentario V1 - Cria diretório para armazenar os gráficos PNG
    path=Path(directory); path.mkdir(parents=True,exist_ok=True)
    # Comentario V1 - Define lista de gráficos a gerar: coluna, título e nome do arquivo
    plots=[("categoria","Atendimentos por categoria","atendimentos_categoria.png"),("status","Atendimentos por status","atendimentos_status.png")]
    # Comentario V1 - Itera sobre cada gráfico a ser gerado
    for column,title,name in plots:
        # Comentario V1 - Conta valores na coluna, ordena crescente e cria gráfico de barras horizontal
        ax=df[column].fillna("Sem informação").value_counts().sort_values().plot.barh(color="#1F4E78",figsize=(9,5))
        # Comentario V1 - Define título, rótulos dos eixos e formata layout
        ax.set_title(title); ax.set_xlabel("Quantidade"); ax.set_ylabel(""); plt.tight_layout()
        # Comentario V1 - Salva figura com alta resolução (160 DPI) e fecha a figura para liberar memória
        plt.savefig(path/name,dpi=160); plt.close()
    # Comentario V1 - Calcula tempo médio por categoria, remove NaN e ordena valores
    temp=df.assign(tempo=pd.to_numeric(df["tempo_minutos"],errors="coerce")).groupby("categoria")["tempo"].mean().dropna().sort_values()
    # Comentario V1 - Cria gráfico de barras horizontal com cores diferentes para tempo médio
    ax=temp.plot.barh(color="#D6A84B",figsize=(9,5))
    # Comentario V1 - Configura título e rótulos do gráfico de tempo
    ax.set_title("Tempo médio por categoria"); ax.set_xlabel("Minutos"); ax.set_ylabel("")
    # Comentario V1 - Salva gráfico e libera recursos
    plt.tight_layout(); plt.savefig(path/"tempo_medio_categoria.png",dpi=160); plt.close()
