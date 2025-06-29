import streamlit as st
import json
import io
from streamlit_sortables import sort_items

# Categories and their colors
CATEGORY_COLORS = {
    "birth": "#99ccff",
    "family": "#b6e6a6",
    "illness": "#ffd699",
    "special": "#e4b7fa",
    "other": "#eeeeee"
}

def load_questions(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_questions(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def render_question(q, i):
    color = CATEGORY_COLORS.get(q.get("category", "other"), "#eeeeee")
    st.markdown(
        f"<div style='background:{color};padding:10px;border-radius:8px;'>"
        f"<b>Q{i+1}:</b> <span>{q['text']}</span><br>"
        f"<small>Category:</small> <b>{q.get('category', 'other')}</b> | "
        f"Priority: <b>{q.get('priority', '')}</b> | "
        f"Required: <b>{'✅' if q.get('required', False) else '—'}</b> | "
        f"Attention: <b>{'⚠️' if q.get('attention', False) else '—'}</b><br>"
        f"<i>{q.get('notes','')}</i>"
        "</div>", unsafe_allow_html=True
    )

def main():
    st.title("📝 Question Editor (Ages & Stages)")

    st.write("**Create, edit, and organize questions for each stage of persona-building.**")

    # File handling
    default_file = "questions_sample.json"
    json_file = st.text_input("Question file", value=default_file, key="json_file")
    if st.button("Load Questions"):
        st.session_state.data = load_questions(json_file)
        st.success("Questions loaded!")
    if "data" not in st.session_state:
        st.session_state.data = load_questions(json_file)

    data = st.session_state.data
    stage_names = list(data.keys())
    # Stage selection/creation
    stage = st.selectbox("Select stage", options=stage_names + ["[Add new stage]"])
    if stage == "[Add new stage]":
        new_stage = st.text_input("Enter new stage name")
        if st.button("Create Stage") and new_stage:
            if new_stage not in data:
                data[new_stage] = {"questions": [], "status": "building"}
                stage = new_stage
                st.success(f"Stage '{new_stage}' created.")
                st.stop()
            else:
                st.warning("Stage already exists.")

    if stage not in data:
        st.info("Select or create a stage to begin.")

    else:
        qs = data[stage]["questions"]
        st.header(f"Questions for: {stage}")
        st.caption(f"Total: {len(qs)}")

        # Reorder
        if len(qs) > 1:
            st.markdown("**Drag to reorder:**")
            reordered = sort_items(
                [f"{q['text']} [{q.get('category', 'other')}, priority {q.get('priority', '')}]" for q in qs],
                direction="vertical",
            )
            # Update order if changed
            if reordered != list(range(len(qs))):
                qs[:] = [qs[i] for i in reordered]
                st.success("Order updated!")

        # Display and edit questions
        for i, q in enumerate(qs):
            with st.expander(f"Q{i+1}: {q['text'][:40]}"):
                col1, col2 = st.columns(2)
                q["text"] = col1.text_area("Question text", value=q["text"], key=f"text_{i}")
                q["category"] = col2.selectbox(
                    "Category", options=list(CATEGORY_COLORS.keys()), index=list(CATEGORY_COLORS.keys()).index(q.get("category", "other")), key=f"cat_{i}"
                )
                q["priority"] = col1.number_input("Priority (lower is higher)", min_value=1, max_value=100, value=int(q.get("priority", i+1)), key=f"prio_{i}")
                q["required"] = col2.checkbox("Required", value=bool(q.get('required', False)), key=f"req_{i}")
                q["attention"] = col2.checkbox("Attention flag", value=bool(q.get('attention', False)), key=f"attn_{i}")
                q["notes"] = col1.text_input("Notes", value=q.get("notes", ""), key=f"note_{i}")

                # Delete
                if st.button(f"Delete Q{i+1}", key=f"del_{i}"):
                    qs.pop(i)
                    st.warning("Question deleted. Please save.")
                    st.stop()

        # Add new question
        st.subheader("Add New Question")
        with st.form("add_q"):
            text = st.text_area("Question text")
            category = st.selectbox("Category", list(CATEGORY_COLORS.keys()), index=0)
            priority = st.number_input("Priority (lower=more important)", 1, 100, value=len(qs)+1)
            required = st.checkbox("Required")
            attention = st.checkbox("Attention flag")
            notes = st.text_input("Notes")
            if st.form_submit_button("Add"):
                qs.append({
                    "text": text,
                    "category": category,
                    "notes": notes,
                    "priority": priority,
                    "required": required,
                    "attention": attention
                })
                st.success("Question added! Please save.")
                st.stop()

        # Save
        if st.button("Save Questions"):
            save_questions(data, json_file)
            st.success(f"Saved to {json_file}")

    st.write("DEBUG - st.session_state.data:", st.session_state.get("data"))

    # Download button is always at the bottom
    st.markdown("---")
    st.subheader("Download Current Questions JSON")
    if "data" in st.session_state and st.session_state.data:
        json_bytes = io.BytesIO(json.dumps(st.session_state.data, indent=2, ensure_ascii=False).encode("utf-8"))
        st.download_button(
            label="⬇️ Download questions JSON",
            data=json_bytes,
            file_name=st.session_state.get("json_file", "questions_sample.json"),
            mime="application/json"
        )
    else:
        st.info("No questions data loaded or available yet to download.")
    st.markdown("---")
    st.caption("Built with 🦊 by Kit for Todd.")

if __name__ == "__main__":
    main()
