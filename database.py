import sqlite3
import json
import os
from datetime import datetime


def create_connection():
    """
    Create database connection
    """
    conn = sqlite3.connect('resume_screener.db')
    return conn


def create_tables():
    """
    Create all required tables
    """
    conn = create_connection()
    cursor = conn.cursor()

    # Create job searches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT NOT NULL,
            job_description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create resume results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resume_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_id INTEGER,
            file_name TEXT,
            candidate_name TEXT,
            email TEXT,
            phone TEXT,
            total_score REAL,
            skills_score REAL,
            experience_score REAL,
            education_score REAL,
            matched_skills TEXT,
            resume_skills TEXT,
            experience_years INTEGER,
            education TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (search_id) REFERENCES job_searches (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database tables created successfully!")


def save_job_search(job_title, job_description):
    """
    Save job search to database
    Returns search_id
    """
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO job_searches (job_title, job_description)
        VALUES (?, ?)
    ''', (job_title, job_description))

    search_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return search_id


def save_resume_results(search_id, ranked_resumes):
    """
    Save all resume results to database
    """
    conn = create_connection()
    cursor = conn.cursor()

    for resume in ranked_resumes:
        cursor.execute('''
            INSERT INTO resume_results (
                search_id, file_name, candidate_name,
                email, phone, total_score, skills_score,
                experience_score, education_score,
                matched_skills, resume_skills,
                experience_years, education
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            search_id,
            resume['file_name'],
            resume['name'],
            resume['email'],
            resume['phone'],
            resume['total_score'],
            resume['skills_score'],
            resume['experience_score'],
            resume['education_score'],
            json.dumps(resume['matched_skills']),
            json.dumps(resume['resume_skills']),
            resume['experience_years'],
            resume['education']
        ))

    conn.commit()
    conn.close()
    print(f"Saved {len(ranked_resumes)} resume results!")


def get_all_searches():
    """
    Get all previous job searches
    """
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, job_title, created_at
        FROM job_searches
        ORDER BY created_at DESC
    ''')

    searches = cursor.fetchall()
    conn.close()

    return searches


def get_search_results(search_id):
    """
    Get results for a specific search
    """
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM resume_results
        WHERE search_id = ?
        ORDER BY total_score DESC
    ''', (search_id,))

    results = cursor.fetchall()
    conn.close()

    return results


def delete_search(search_id):
    """
    Delete a search and its results
    """
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        'DELETE FROM resume_results WHERE search_id = ?',
        (search_id,)
    )
    cursor.execute(
        'DELETE FROM job_searches WHERE id = ?',
        (search_id,)
    )

    conn.commit()
    conn.close()
    print(f"Deleted search {search_id}")