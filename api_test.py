import requests
import streamlit as st
import json

def test_fastapi_endpoints():
    """Test FastAPI endpoints from Streamlit"""
    
    st.title("FastAPI Integration Test")
    st.write("Testing the PersonaPath FastAPI endpoints:")
    
    base_url = "http://localhost:8000"
    
    # Test root endpoint
    st.subheader("1. Root Endpoint Test")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            st.success("✅ Root endpoint working")
            st.json(response.json())
        else:
            st.error(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Connection error: {e}")
    
    # Test health endpoint
    st.subheader("2. Health Check")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            st.success("✅ Health check working")
            st.json(response.json())
        else:
            st.error(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Health check error: {e}")
    
    # Test jobs endpoint
    st.subheader("3. Jobs Endpoint")
    try:
        response = requests.get(f"{base_url}/jobs")
        if response.status_code == 200:
            st.success("✅ Jobs endpoint working")
            data = response.json()
            st.write(f"Found {len(data.get('jobs', []))} job roles")
            if data.get('jobs'):
                st.json(data['jobs'][0])  # Show first job
        else:
            st.error(f"❌ Jobs endpoint failed: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Jobs endpoint error: {e}")
    
    # Test skill categories
    st.subheader("4. Skill Categories")
    try:
        response = requests.get(f"{base_url}/skills/categories")
        if response.status_code == 200:
            st.success("✅ Skill categories working")
            data = response.json()
            st.json(data['categories'])
        else:
            st.error(f"❌ Skill categories failed: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Skill categories error: {e}")
    
    # Test career paths
    st.subheader("5. Career Paths")
    try:
        response = requests.get(f"{base_url}/career/paths")
        if response.status_code == 200:
            st.success("✅ Career paths working")
            data = response.json()
            st.json(data['career_paths'])
        else:
            st.error(f"❌ Career paths failed: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Career paths error: {e}")
    
    # Test mentors
    st.subheader("6. Mentors")
    try:
        response = requests.get(f"{base_url}/mentors")
        if response.status_code == 200:
            st.success("✅ Mentors endpoint working")
            data = response.json()
            st.write(f"Found {len(data.get('mentors', []))} mentors")
            if data.get('mentors'):
                st.json(data['mentors'][0])  # Show first mentor
        else:
            st.error(f"❌ Mentors endpoint failed: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Mentors endpoint error: {e}")
    
    # Interactive API test section
    st.subheader("7. Interactive Chat Test")
    chat_message = st.text_input("Enter a message to test the chat API:")
    if st.button("Send Message") and chat_message:
        try:
            response = requests.post(
                f"{base_url}/chat",
                json={"message": chat_message}
            )
            if response.status_code == 200:
                st.success("✅ Chat API working")
                data = response.json()
                st.write("**Response:**")
                st.write(data.get('response', 'No response'))
            else:
                st.error(f"❌ Chat API failed: {response.status_code}")
                st.write(response.text)
        except Exception as e:
            st.error(f"❌ Chat API error: {e}")

if __name__ == "__main__":
    test_fastapi_endpoints()