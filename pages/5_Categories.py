import streamlit as st
import requests
from utils.auth import get_headers, require_role

require_role("admin")

st.set_page_config(page_title="Categories", page_icon="📂")

st.title("📂 Category Management")

BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000")
headers = get_headers()

# Initialize session state
if "editing_category" not in st.session_state:
    st.session_state["editing_category"] = None

tab1, tab2 = st.tabs(["➕ Create", "📋 View All"])

with tab1:
    st.subheader("Create New Category")
    
    with st.form("create_category_form", clear_on_submit=True):
        name = st.text_input("Category Name", placeholder="e.g., Technical Support")
        description = st.text_area("Description", placeholder="Brief description")
        
        submit = st.form_submit_button("Create Category", use_container_width=True)
        
        if submit:
            if not name:
                st.error("Category name is required!")
            else:
                try:
                    response = requests.post(
                        f"{BASE_URL}/categories",
                        headers=headers,
                        json={
                            "name": name,
                            "description": description or None
                        }
                    )
                    if response.status_code == 200:
                        st.success("✅ Category created successfully!")
                        st.session_state["categories"] = []
                        st.rerun()
                    else:
                        error = response.json().get("detail", "Unknown error")
                        st.error(f"Failed: {error}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

with tab2:
    st.subheader("All Categories")
    
    try:
        # Fetch ALL categories (including inactive ones for admin)
        response = requests.get(f"{BASE_URL}/fetch/categories", headers=headers)
        if response.status_code == 200:
            categories = response.json()
            if categories:
                for cat in categories:
                    is_editing = (st.session_state.get("editing_category") and 
                                 st.session_state["editing_category"]["category_id"] == cat['category_id'])
                    
                    if is_editing:
                        # Edit mode
                        st.divider()
                        with st.container(border=True):
                            st.subheader(f"✏️ Editing: {cat['name']}")
                            
                            with st.form(f"edit_category_form_{cat['category_id']}"):
                                edit_name = st.text_input("Category Name", value=cat['name'])
                                edit_description = st.text_area("Description", value=cat.get('description', ''))
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    update_submit = st.form_submit_button("💾 Update Category", use_container_width=True)
                                with col2:
                                    cancel_submit = st.form_submit_button("❌ Cancel", use_container_width=True)
                                
                                if update_submit:
                                    if not edit_name:
                                        st.error("Category name is required!")
                                    else:
                                        try:
                                            update_response = requests.patch(
                                                f"{BASE_URL}/update/category",
                                                headers=headers,
                                                json={
                                                    "id": cat['category_id'],
                                                    "name": edit_name,
                                                    "description": edit_description or None
                                                }
                                            )
                                            
                                            if update_response.status_code == 200:
                                                st.success("✅ Category updated successfully!")
                                                st.session_state["editing_category"] = None
                                                st.session_state["categories"] = []
                                                st.rerun()
                                            else:
                                                error_detail = update_response.json().get("detail", "Unknown error")
                                                st.error(f"Update failed: {error_detail}")
                                        except Exception as e:
                                            st.error(f"Error: {str(e)}")
                                
                                if cancel_submit:
                                    st.session_state["editing_category"] = None
                                    st.rerun()
                    else:
                        # View mode
                        status_icon = "✅" if cat.get('is_active') else "❌ (Inactive)"
                        with st.expander(f"📁 {cat['name']} - {status_icon}", expanded=False):
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.write("**ID:**", cat['category_id'])
                                st.write("**Description:**", cat.get('description', 'No description'))
                                st.write("**Status:**", "Active ✅" if cat.get('is_active') else "Inactive ❌")
                                st.write("**Created:**", cat['created_at'])
                                if cat.get('updated_at'):
                                    st.write("**Updated:**", cat['updated_at'])
                            
                            with col2:
                                # Edit button
                                if st.button(f"✏️ Edit", key=f"edit_{cat['category_id']}", use_container_width=True):
                                    st.session_state["editing_category"] = cat
                                    st.rerun()
                                
                                # Reactivate button (only for inactive categories)
                                if not cat.get('is_active'):
                                    if st.button(f"🔄 Reactivate", key=f"reactivate_{cat['category_id']}", use_container_width=True):
                                        try:
                                            reactivate_response = requests.patch(
                                                f"{BASE_URL}/reactivate/category/{cat['category_id']}",
                                                headers=headers
                                            )
                                            if reactivate_response.status_code == 200:
                                                st.success("✅ Category reactivated successfully!")
                                                st.session_state["categories"] = []
                                                st.rerun()
                                            else:
                                                st.error("Failed to reactivate category")
                                        except Exception as e:
                                            st.error(f"Error: {str(e)}")
                                else:
                                    # Delete button (only for active categories)
                                    if st.button(f"🗑️ Delete", key=f"delete_{cat['category_id']}", use_container_width=True):
                                        st.session_state["delete_category_id"] = cat['category_id']
                                        st.session_state["delete_category_name"] = cat['name']
                                        st.rerun()
            else:
                st.info("No categories found")
        else:
            st.warning("Could not fetch categories")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Delete confirmation dialog
if "delete_category_id" in st.session_state:
    cat_id = st.session_state["delete_category_id"]
    cat_name = st.session_state.get("delete_category_name", "this category")
    
    st.divider()
    with st.container(border=True):
        st.warning(f"⚠️ Delete Category: '{cat_name}'")
        st.caption("This will deactivate the category. Categories with associated tickets may not be deletable.")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("✅ Yes, Delete", use_container_width=True):
                try:
                    delete_response = requests.delete(
                        f"{BASE_URL}/delete/category/{cat_id}",
                        headers=headers
                    )
                    if delete_response.status_code == 200:
                        st.success("✅ Category deleted successfully!")
                        del st.session_state["delete_category_id"]
                        if "delete_category_name" in st.session_state:
                            del st.session_state["delete_category_name"]
                        st.session_state["categories"] = []
                        st.rerun()
                    else:
                        error_detail = delete_response.json().get("detail", "Unknown error")
                        st.error(f"Delete failed: {error_detail}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                del st.session_state["delete_category_id"]
                if "delete_category_name" in st.session_state:
                    del st.session_state["delete_category_name"]
                st.rerun()