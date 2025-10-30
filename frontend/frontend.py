import streamlit as st
import difflib
import re
import pyperclip
from typing import List, Tuple
from api import correct_text

def generate_word_diff(original: str, revised: str) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
    """
    Generate word-level diff between original and revised text.
    Returns: (original_diff, revised_diff) where each is a list of (word, status) tuples
    Status can be: 'unchanged', 'deleted', 'added', 'modified'
    """
    # Split into words while preserving whitespace
    original_words = re.findall(r'\S+|\s+', original)
    revised_words = re.findall(r'\S+|\s+', revised)

    # Use difflib to get sequence matching
    matcher = difflib.SequenceMatcher(None, original_words, revised_words)

    original_diff = []
    revised_diff = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            # Unchanged text
            for i in range(i1, i2):
                original_diff.append((original_words[i], 'unchanged'))
            for j in range(j1, j2):
                revised_diff.append((revised_words[j], 'unchanged'))
        elif tag == 'delete':
            # Text deleted from original
            for i in range(i1, i2):
                original_diff.append((original_words[i], 'deleted'))
        elif tag == 'insert':
            # Text added in revised
            for j in range(j1, j2):
                revised_diff.append((revised_words[j], 'added'))
        elif tag == 'replace':
            # Text modified
            for i in range(i1, i2):
                original_diff.append((original_words[i], 'modified'))
            for j in range(j1, j2):
                revised_diff.append((revised_words[j], 'modified'))

    return original_diff, revised_diff


def render_diff_text(diff_data: List[Tuple[str, str]], title: str):
    """Render diff text with appropriate styling"""
    st.markdown(f"**{title}**")

    # Create HTML with color coding optimized for dark background
    html_content = []
    for word, status in diff_data:
        if status == 'unchanged':
            html_content.append(f'<span>{word}</span>')
        elif status == 'deleted':
            html_content.append(
                f'<span style="background-color: #4a1a1a; color: #ff6b6b; text-decoration: line-through;">{word}</span>')
        elif status == 'added':
            html_content.append(f'<span style="background-color: #1a4a1a; color: #51cf66;">{word}</span>')
        elif status == 'modified':
            html_content.append(f'<span style="background-color: #4a3a1a; color: #ffd43b;">{word}</span>')

    # Wrap in a scrollable div with dark theme
    full_html = f'''
    <div style="
        border: 1px solid #333; 
        padding: 15px; 
        max-height: 300px; 
        overflow-y: auto; 
        background-color: #1a1a1a;
        color: #e0e0e0;
        font-family: 'Arial', monospace;
        font-size: 14px;
        line-height: 1.6;
        white-space: pre-wrap;
        border-radius: 5px;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.3);
    ">
        {''.join(html_content)}
    </div>
    '''

    st.markdown(full_html, unsafe_allow_html=True)


# Main Streamlit App
st.title("LLM Writing Assistant")

# Input section
st.subheader("Input")

# Auto-fill with sample text if selected
initial_text = ""
if hasattr(st.session_state, 'sample_text'):
    initial_text = st.session_state.sample_text
    # Clear the sample text to avoid persistence
    del st.session_state.sample_text

original_text = st.text_area("Enter your report draft here:", value=initial_text, height=200, key="original_input")

# Controls section
st.subheader("Assistance Options")

col1, col2 = st.columns(2)

with col1:
    mode = st.radio(
        "Select correction mode:",
        options=["full", "grammar"],
        index=0,
        help="Full mode improves content and style and Grammar mode only fixes grammar errors."
    )

with col2:
    st.markdown("**Color Legend:**")
    st.markdown("""
    <div style="
        font-size: 12px; 
        background-color: #1a1a1a; 
        padding: 12px; 
        border-radius: 5px; 
        border: 1px solid #333;
        color: #e0e0e0;
    ">
    <span style="background-color: #1a4a1a; color: #51cf66; padding: 3px 6px; border-radius: 3px;">■ Added</span><br><br>
    <span style="background-color: #4a3a1a; color: #ffd43b; padding: 3px 6px; border-radius: 3px;">■ Modified</span><br><br>
    <span style="background-color: #4a1a1a; color: #ff6b6b; padding: 3px 6px; border-radius: 3px; text-decoration: line-through;">■ Deleted</span>
    </div>
    """, unsafe_allow_html=True)

# Process button
if st.button("Get Assistance", type="primary"):
    if not original_text.strip():
        st.warning("Please enter some text first.")
    else:
        with st.spinner("Processing your text..."):
            # Simulate LLM processing
            assisted_text = correct_text(input_text=original_text, mode=mode)

            # Store results in session state for persistence
            st.session_state.original_text = original_text
            st.session_state.assisted_text = assisted_text

# Display results if available
if hasattr(st.session_state, 'assisted_text'):
    st.subheader("Results")

    # Copyable revised text with direct copy button
    st.markdown("**Revised Text:**")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.text_area(
            "Revised text:",
            value=st.session_state.assisted_text,
            height=150,
            help="You can select text manually or use the Copy button nearby.",
            key="revised_text_area"
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
        if st.button("📋 Copy Text", type="primary", help="Copy revised text to clipboard"):
            try:
                pyperclip.copy(st.session_state.assisted_text)
                st.success("✅ Text copied to clipboard!")
            except Exception as e:
                st.error(f"❌ Copy failed: {str(e)}")
                st.info("💡 Try selecting the text manually and using Ctrl+C")

    # Diff viewer
    st.subheader("Side-by-Side Diff Viewer")

    if st.session_state.original_text != st.session_state.assisted_text:
        # Generate diff
        original_diff, revised_diff = generate_word_diff(
            st.session_state.original_text,
            st.session_state.assisted_text
        )

        # Display side by side
        col1, col2 = st.columns(2)

        with col1:
            render_diff_text(original_diff, "Original Text")

        with col2:
            render_diff_text(revised_diff, "Revised Text")

        # Statistics
        st.subheader("Change Summary")

        # Count changes
        added_count = sum(1 for _, status in revised_diff if status == 'added')
        deleted_count = sum(1 for _, status in original_diff if status == 'deleted')
        modified_count = sum(1 for _, status in revised_diff if status == 'modified')

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Added", added_count, delta=added_count if added_count > 0 else None)
        with col2:
            st.metric("Modified", modified_count, delta=modified_count if modified_count > 0 else None)
        with col3:
            st.metric("Deleted", deleted_count, delta=-deleted_count if deleted_count > 0 else None)

    else:
        st.info("No changes detected between original and revised text.")

    # Export options with enhanced copy functionality
    st.subheader("Export & Copy Options")

    col1, col2, col3 = st.columns(3)

    # Ensure diffs are always defined
    original_diff = []
    revised_diff = []

    with col1:
        # Direct copy button for revised text
        if st.button("📋 Quick Copy", help="Copy revised text directly to clipboard"):
            try:
                pyperclip.copy(st.session_state.assisted_text)
                st.success("✅ Copied!")
            except Exception as e:
                st.error("❌ Copy failed")

    with col2:
        # Download revised text
        st.download_button(
            label="💾 Download Text",
            data=st.session_state.assisted_text,
            file_name="revised_text.txt",
            mime="text/plain"
        )

    with col3:
        # Download comparison report
        comparison_report = f"""ORIGINAL TEXT:
{st.session_state.original_text}

REVISED TEXT:
{st.session_state.assisted_text}

CHANGES SUMMARY:
- Mode used: {mode}
- Added words: {sum(1 for _, status in revised_diff if status == 'added')}
- Modified words: {sum(1 for _, status in revised_diff if status == 'modified')}
- Deleted words: {sum(1 for _, status in original_diff if status == 'deleted')}
"""

        st.download_button(
            label="📊 Download Report",
            data=comparison_report,
            file_name="comparison_report.txt",
            mime="text/plain"
        )

# Instructions
with st.expander("How to use this tool"):
    st.markdown("""
    1. **Enter your text** in the input area above
    2. **Choose a correction mode**:
       - **Grammar**: Fixes only grammar and spelling errors
       - **Full**: Improves grammar, style, and content
    3. **Click "Get Assistance"** to process your text
    4. **Review the results**:
       - The revised text appears in a copyable text area
       - The diff viewer shows changes side-by-side with color coding
       - Change statistics summarize the modifications
    5. **Export your work** using the download buttons

    **Color Legend:**
    - 🟢 Green: Added text
    - 🟠 Orange: Modified text  
    - 🔴 Red: Deleted text (strikethrough)
    """)

st.markdown("---")