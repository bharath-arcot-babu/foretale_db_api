import time
from api.database.db_service import DatabaseService
from tests.p2pdup00101 import P2PDUP00101

class TaskExecutor:
    def __init__(self):
        self.db_service = DatabaseService()
    
    def fetch_pending_tasks(self):
        procedure_name = "dbo.SPROC_GET_TEST_RUN_HISTORY_BY_STATUS" 
        params = {}
        tasks = self.db_service.execute_stored_procedure(procedure_name, params, isCommit=False)
        print(tasks)
        return tasks.get("data", [])
    
    def update_task_status(self, run_id, status, message, error_message=None, error_stack_trace=None, error_source=None, severity_level=None, request_path=None):
        procedure_name = "dbo.SPROC_UPDATE_TEST_RUN_HISTORY"
        params = {
            "run_id": run_id, 
            "status": status, 
            "message": message,
            "error_message": error_message,
            "error_stack_trace": error_stack_trace,
            "error_source": error_source,
            "severity_level": severity_level,
            "request_path": request_path

            }
        self.db_service.execute_stored_procedure(procedure_name, params, isCommit=True)

    def process_task(self, task):
        run_id = task["run_id"]
        test_code = task["test_code"]
        test_name = task["test_name"]
        project_test_id = task["project_test_id"]
        test_config = task["config"]

        try:
            print(test_code)
            obj = P2PDUP00101(project_test_id = project_test_id)
            obj.process_items()
            self.update_task_status(run_id, "Completed")
        except Exception as e:
            try:
                error_message = str(e)
                error_stack_trace = str(e)
                error_source = "TaskExecutor.process_task"
                severity_level = "High"
                request_path = "execute_task.py"
                self.update_task_status(run_id, "Failed", "{0} - Test Failed".format(test_code), error_message, error_stack_trace, error_source, severity_level, request_path)
            except Exception as e:
                pass


    def run(self):
        while True:
            try:
                tasks = self.fetch_pending_tasks()
                print(tasks)
                
                if not tasks:
                    time.sleep(10)  # Wait for 10 seconds before checking again
                    continue
                
                for task in tasks:
                    self.process_task(task)

                time.sleep(10)  # Wait for 10 seconds before the next execution cycle

            except Exception as e:
                print(str(e))
                time.sleep(10)

if __name__ == "__main__":
    executor = TaskExecutor()
    executor.run()
