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
		ck.checkin_at,
		REGEXP_REPLACE(ck.check_in_content, '<[^>]*>', '') as check_in_content,
		u.FullName as checkin_by,
		ck.progress
	FROM
		t_key_results AS kr
		LEFT JOIN ( SELECT *, ROW_NUMBER() OVER ( PARTITION BY key_result_id ORDER BY checkin_at DESC ) AS order_rank FROM checks_in WHERE deleted_at IS NULL ) AS ck ON ck.key_result_id = kr.key_result_id 
		JOIN users u on u.id = ck.created_by
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
		objective_name,
		objective_start,
		objective_end,
		objective_description,
		u.FullName as created_by
	FROM
		t_objectives
        JOIN users u on u.id = t_objectives.created_by
    WHERE
		objective_id = {object_id}
		AND t_objectives.deleted_at IS NULL; """, include_columns = True)

tools = [get_objective_data, get_last_two_check_in_key_result]