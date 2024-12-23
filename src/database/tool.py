from langchain_core.tools import tool
from src.database.connector import get_knowledge_db

db= get_knowledge_db()
@tool
def get_last_two_check_in_key_result(object_id):
    """Get last two check in of each key result from objective with object_id.
    Args:
        object_id: first int
    """
    return db.run(f""" SELECT
		kr.key_result_content,
		kr.key_result_start,
		kr.key_result_end,
        o.objective_name,
		ck.checkin_at,
		REGEXP_REPLACE(ck.check_in_content, '<[^>]*>', '') as check_in_content,
		ck.progress
	FROM
		t_key_results AS kr
		LEFT JOIN ( SELECT *, ROW_NUMBER() OVER ( PARTITION BY key_result_id ORDER BY checkin_at DESC ) AS order_rank FROM checks_in WHERE deleted_at IS NULL ) AS ck ON ck.key_result_id = kr.key_result_id 
		JOIN t_objectives o on o.objective_id = kr.objective_id
    WHERE
		(ck.order_rank <= 2 OR ck.order_rank is NULL)
		AND kr.objective_id = {object_id}
		AND kr.deleted_at IS NULL; """, include_columns = True)

@tool
def get_objective_data(object_id):
    """Get data of objective with object_id.
    Args:
        object_id: first int
    """
    return db.run(f""" SELECT
		*,
		Null as created_at,
        Null as updated_at,
        Null as created_by,
        Null as updated_by
	FROM
		t_objectives
    WHERE
		objective_id = {object_id}
		AND deleted_at IS NULL; """, include_columns = True)

tools = [get_objective_data, get_last_two_check_in_key_result]