import os
from app.services.supabase_client import supabase

def run_migrations():
    # Read the migration file
    migration_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'migrations', '001_create_documents_table.sql')
    
    with open(migration_path, 'r') as f:
        sql = f.read()
    
    try:
        # Execute the migration
        result = supabase.table('documents').execute(sql)
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Error running migration: {str(e)}")
        raise

if __name__ == "__main__":
    run_migrations() 