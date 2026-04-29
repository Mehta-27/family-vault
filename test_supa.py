from supabase import create_client
import toml

secrets = toml.load('.streamlit/secrets.toml')
url = secrets['supabase']['url']
key = secrets['supabase']['key']
supabase = create_client(url, key)

try:
    res = supabase.table('assets').select("*").execute()
    print("SUCCESS:", res)
except Exception as e:
    print("ERROR:", e)
