-- Habilitar a extensão pgvector
create extension if not exists vector;

-- Remove objetos anteriores se existirem
drop function if exists match_documents;
drop table if exists documents;

-- Tabela de chunks com embeddings (id uuid gerado automaticamente)
create table documents (
    id        uuid primary key default gen_random_uuid(),
    content   text,
    metadata  jsonb,
    embedding vector(1536)
);

-- Função de busca por similaridade (cosine distance)
create or replace function match_documents (
    query_embedding vector(1536),
    match_count     int   default null,
    filter          jsonb default '{}'
) returns table (
    id         uuid,
    content    text,
    metadata   jsonb,
    similarity float
)
language plpgsql
as $$
#variable_conflict use_column
begin
    return query
    select
        id,
        content,
        metadata,
        1 - (documents.embedding <=> query_embedding) as similarity
    from documents
    where metadata @> filter
    order by documents.embedding <=> query_embedding
    limit match_count;
end;
$$;
