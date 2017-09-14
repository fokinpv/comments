from sqlalchemy import text


insert_into_tree = text(
    'INSERT INTO comment_path(parent_id, child_id, level) '
    'SELECT parent_id, :child_id, p.level + 1 '
    'FROM  comment_path p '
    'WHERE p.child_id = :parent_id '
    'UNION ALL SELECT :child_id, :child_id, 0'
)

select_all_comments = text(
    'SELECT '
    'comment.id, comment.parent_id, '
    'comment.created_at, comment.updated_at, comment.text '
    'FROM comment '
    'JOIN comment_path tree ON comment.id = tree.child_id '
    'WHERE tree.parent_id = :comment_id'
)
