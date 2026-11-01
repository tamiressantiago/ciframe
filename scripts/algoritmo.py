#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from musica import Musica

# Same as backend
ARTISTA_ID = 0
MUSICA_ID = 1
ARTISTA = 2
MUSICA = 3
GENERO = 4
POPULARIDADE = 5
TOM = 6
SEQ_FAMOSA = 7
CIFRA = 8

sequencias = {'BmGDA' : 0,
        'CGAmF' : 1,
        'EmG' : 2,
        'CA7DmG7' : 3,
        'GmF' : 4,
        'CC7FFm' : 5}


def limpa_cifra(raw_cifra):
    cifra = []
    for m in raw_cifra:
        if m.strip() != '':
            if '|' in m:
                acorde = m.split('|')[0].split()[0]
                cifra.append(acorde)
            else:
                tokens = [token for token in m.split()]
                cifra += tokens
    return cifra


def split_key_to_tokens(key):
    res = []
    i = 0
    n = len(key)
    while i < n:
        c = key[i]
        if i + 1 < n and key[i + 1] == 'm' and c.isupper():
            res.append(key[i:i+2])
            i += 2
            continue
        if i + 1 < n and key[i + 1] == '7' and c.isupper():
            res.append(key[i:i+2])
            i += 2
            continue
        if i + 1 < n and key[i + 1] == '#':
            if i + 2 < n and key[i + 2] == 'm':
                res.append(key[i:i+3])
                i += 3
                continue
            res.append(key[i:i+2])
            i += 2
            continue
        if c.isupper() or c.islower():
            res.append(c)
            i += 1
            continue
        i += 1
    return res


def has_exact_consecutive_sequence(cifra_list, seq_tokens):
    if len(seq_tokens) == 0:
        return False
    if len(seq_tokens) > len(cifra_list):
        return False
    for i in range(len(cifra_list) - len(seq_tokens) + 1):
        match = True
        for j in range(len(seq_tokens)):
            if cifra_list[i + j].strip() != seq_tokens[j]:
                match = False
                break
        if match:
            return True
    return False


def musica_contem_sequencia(cifra, seq_tokens):
    if not has_exact_consecutive_sequence(cifra, seq_tokens):
        return False
    seq_chords_set = set(seq_tokens)
    cifra_chords_set = set([c.strip() for c in cifra if str(c).strip() != ''])
    extra = cifra_chords_set - seq_chords_set
    if len(extra) == 0:
        return True
    return False


def main():
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'top', 'dataset_final.csv')
    musicas_dict = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        f.readline()
        for line in f:
            try:
                line = line.replace('"', '').replace('NA', '')[:-1]
            except:
                continue
            musica = line.split(',')
            if len(musica) < 9:
                continue
            try:
                musica[POPULARIDADE] = int(str(musica[POPULARIDADE]).replace('.', ''))
            except:
                musica[POPULARIDADE] = 0
            if musica[CIFRA] != '':
                musica[CIFRA] = limpa_cifra(musica[CIFRA].split(';'))
            else:
                musica[CIFRA] = []
            musica[SEQ_FAMOSA] = str(musica[SEQ_FAMOSA]).split(';')
            musica_obj = Musica(musica[ARTISTA_ID], musica[ARTISTA],
                    musica[MUSICA_ID], musica[MUSICA], musica[GENERO],
                    int(musica[POPULARIDADE]), musica[SEQ_FAMOSA],
                    musica[TOM], musica[CIFRA])
            musicas_dict[musica_obj.id_unico_musica] = musica_obj
    
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append("VALIDAÇÃO: ALGORITMO DE BUSCA POR SEQUÊNCIA EXATA E CONSECUTIVA")
    output_lines.append("GABARITO: APENAS músicas com tag SEQ_FAMOSA correspondente (sem filtro adicional)")
    output_lines.append("ALGORITMO: musica_contem_sequencia(cifra, seq_tokens)")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    for seq_key, seq_id in sorted(sequencias.items(), key=lambda x: x[1]):
        seq_tokens = split_key_to_tokens(seq_key)
        seq_chords_set = set(seq_tokens)
        
        # Expected: APENAS músicas com a tag SEQ_FAMOSA correspondente
        esperados = []
        for mid, m in musicas_dict.items():
            for sf in m.seqs_famosas:
                sf_clean = str(sf).strip()
                if sf_clean == str(seq_id):
                    esperados.append(mid)
                    break
        
        # Found by algoritmo
        encontrados = []
        for mid, m in musicas_dict.items():
            if musica_contem_sequencia(m.cifra, seq_tokens):
                encontrados.append(mid)
        
        esperados_set = set(esperados)
        encontrados_set = set(encontrados)
        
        falsos_positivos = encontrados_set - esperados_set
        falsos_negativos = esperados_set - encontrados_set
        verdadeiros_positivos = esperados_set & encontrados_set
        
        precisao = len(verdadeiros_positivos) / len(encontrados_set) if encontrados_set else 0.0
        recall = len(verdadeiros_positivos) / len(esperados_set) if esperados_set else 0.0
        
        output_lines.append(f"SEQUÊNCIA: {seq_key} (id={seq_id}) | Tokens: {seq_tokens} | Chords_set: {sorted(list(seq_chords_set))}")
        output_lines.append("-" * 80)
        output_lines.append(f"Total esperado (apenas tag): {len(esperados_set)}")
        output_lines.append(f"Total encontrado (algoritmo): {len(encontrados_set)}")
        output_lines.append(f"Verdadeiros positivos: {len(verdadeiros_positivos)}")
        output_lines.append(f"Falsos positivos: {len(falsos_positivos)}")
        output_lines.append(f"Falsos negativos: {len(falsos_negativos)}")
        output_lines.append(f"Precisão: {precisao:.4f} | Recall: {recall:.4f}")
        output_lines.append("")
        
        if falsos_positivos:
            output_lines.append(f"  Falsos positivos (até 5):")
            for i, mid in enumerate(list(falsos_positivos)[:5]):
                m = musicas_dict[mid]
                output_lines.append(f"    {i+1}. {mid} - {m.nome_artista} - {m.nome_musica} | tags: {m.seqs_famosas}")
            output_lines.append("")
        if falsos_negativos:
            output_lines.append(f"  Falsos negativos (até 5):")
            for i, mid in enumerate(list(falsos_negativos)[:5]):
                m = musicas_dict[mid]
                output_lines.append(f"    {i+1}. {mid} - {m.nome_artista} - {m.nome_musica} | tags: {m.seqs_famosas}")
                cifra_str = ';'.join(m.cifra[:40])
                output_lines.append(f"       CIFRA(início): {cifra_str}")
            output_lines.append("")
        output_lines.append("")
    
    output_lines.append("=" * 80)
    output_lines.append("FIM DA VALIDAÇÃO")
    output_lines.append("=" * 80)
    
    output = '\n'.join(output_lines)
    print(output)
    
    out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'research', 'saida_validacao_matching.txt')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)
    print(f"\n\nSalvo em: {out_path}")


if __name__ == '__main__':
    main()
