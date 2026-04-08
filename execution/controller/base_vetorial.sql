-- Habilitar a extensão pgvector
create extension if not exists vector;

-- Tabela de chunks com embeddings
create table documents (
    id   bigserial primary key,
    content  text,
    metadata jsonb,
    embedding vector(1536)
);

-- Função de busca por similaridade (cosine distance)
create or replace function match_documents (
    query_embedding vector(1536),
    match_count     int     default null,
    filter          jsonb   default '{}'
) returns table (
    id         bigint,
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
