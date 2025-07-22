-- HireSmart AI Database Initialization Script

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS hiresmart_db;

-- Use the database
\c hiresmart_db;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone_number VARCHAR(20),
    profile_picture VARCHAR(500),
    bio TEXT,
    current_position VARCHAR(255),
    experience_years INTEGER DEFAULT 0,
    skills JSONB,
    education JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Create resumes table
CREATE TABLE IF NOT EXISTS resumes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_path VARCHAR(500),
    parsed_content JSONB,
    skills JSONB,
    experience JSONB,
    education JSONB,
    certifications JSONB,
    file_name VARCHAR(255),
    file_size INTEGER,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create job_descriptions table
CREATE TABLE IF NOT EXISTS job_descriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    description TEXT NOT NULL,
    requirements JSONB,
    skills_required JSONB,
    experience_level VARCHAR(50),
    key_responsibilities JSONB,
    qualifications JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create interview_sessions table
CREATE TABLE IF NOT EXISTS interview_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_description_id INTEGER REFERENCES job_descriptions(id),
    session_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    interview_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'scheduled',
    scheduled_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    duration_minutes INTEGER,
    video_path VARCHAR(500),
    audio_path VARCHAR(500),
    transcript TEXT,
    overall_score FLOAT,
    confidence_score FLOAT,
    communication_score FLOAT,
    technical_score FLOAT,
    analysis_data JSONB,
    feedback_summary TEXT,
    improvement_suggestions JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create interview_questions table
CREATE TABLE IF NOT EXISTS interview_questions (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL,
    category VARCHAR(100),
    difficulty_level VARCHAR(20),
    asked_at TIMESTAMP WITH TIME ZONE,
    response_start_time TIMESTAMP WITH TIME ZONE,
    response_end_time TIMESTAMP WITH TIME ZONE,
    response_duration_seconds INTEGER,
    user_response TEXT,
    response_transcript TEXT,
    content_score FLOAT,
    clarity_score FLOAT,
    relevance_score FLOAT,
    structure_score FLOAT,
    analysis_data JSONB,
    feedback TEXT,
    suggested_improvements JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create real_time_analysis table
CREATE TABLE IF NOT EXISTS real_time_analysis (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    analysis_type VARCHAR(50) NOT NULL,
    confidence_level FLOAT,
    emotion_detected VARCHAR(50),
    facial_expression_data JSONB,
    vocal_analysis_data JSONB,
    posture_data JSONB,
    eye_contact_score FLOAT,
    speaking_pace FLOAT,
    filler_words_count INTEGER DEFAULT 0,
    volume_level FLOAT,
    alert_triggered BOOLEAN DEFAULT FALSE,
    alert_type VARCHAR(50),
    feedback_message VARCHAR(500),
    raw_analysis_data JSONB
);

-- Create assessments table
CREATE TABLE IF NOT EXISTS assessments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assessment_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    assessment_type VARCHAR(50) NOT NULL,
    category VARCHAR(100),
    difficulty_level VARCHAR(20) NOT NULL,
    time_limit_minutes INTEGER NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE,
    submitted_at TIMESTAMP WITH TIME ZONE,
    time_taken_minutes INTEGER,
    status VARCHAR(50) DEFAULT 'not_started',
    overall_score FLOAT,
    max_possible_score FLOAT NOT NULL,
    percentage_score FLOAT,
    results_data JSONB,
    feedback TEXT,
    ai_review TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create coding_problems table
CREATE TABLE IF NOT EXISTS coding_problems (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    difficulty VARCHAR(20) NOT NULL,
    category VARCHAR(100),
    time_limit_seconds INTEGER DEFAULT 30,
    memory_limit_mb INTEGER DEFAULT 128,
    allowed_languages JSONB,
    sample_input TEXT,
    sample_output TEXT,
    test_cases JSONB NOT NULL,
    user_code TEXT,
    programming_language VARCHAR(50),
    submission_time TIMESTAMP WITH TIME ZONE,
    execution_status VARCHAR(50),
    test_cases_passed INTEGER DEFAULT 0,
    total_test_cases INTEGER NOT NULL,
    execution_time_ms INTEGER,
    memory_used_mb FLOAT,
    code_quality_score FLOAT,
    time_complexity VARCHAR(50),
    space_complexity VARCHAR(50),
    code_review_feedback TEXT,
    suggested_improvements JSONB,
    execution_results JSONB,
    error_messages JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create mcq_questions table
CREATE TABLE IF NOT EXISTS mcq_questions (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL,
    category VARCHAR(100),
    difficulty VARCHAR(20) NOT NULL,
    options JSONB NOT NULL,
    correct_answer VARCHAR(10) NOT NULL,
    user_answer VARCHAR(10),
    time_allocated_seconds INTEGER DEFAULT 60,
    time_taken_seconds INTEGER,
    answered_at TIMESTAMP WITH TIME ZONE,
    is_correct BOOLEAN,
    points_awarded FLOAT DEFAULT 0.0,
    max_points FLOAT DEFAULT 1.0,
    explanation TEXT,
    detailed_solution TEXT,
    learning_resources JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_job_descriptions_user_id ON job_descriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_interview_sessions_user_id ON interview_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_interview_sessions_session_id ON interview_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_interview_questions_session_id ON interview_questions(session_id);
CREATE INDEX IF NOT EXISTS idx_real_time_analysis_session_id ON real_time_analysis(session_id);
CREATE INDEX IF NOT EXISTS idx_assessments_user_id ON assessments(user_id);
CREATE INDEX IF NOT EXISTS idx_assessments_assessment_id ON assessments(assessment_id);
CREATE INDEX IF NOT EXISTS idx_coding_problems_assessment_id ON coding_problems(assessment_id);
CREATE INDEX IF NOT EXISTS idx_mcq_questions_assessment_id ON mcq_questions(assessment_id);

-- Insert sample data for testing
INSERT INTO users (email, username, hashed_password, full_name, is_active, is_verified) VALUES
('demo@hiresmart.ai', 'demo_user', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5S/kS', 'Demo User', TRUE, TRUE)
ON CONFLICT (email) DO NOTHING;

-- Create a function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_job_descriptions_updated_at BEFORE UPDATE ON job_descriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_interview_sessions_updated_at BEFORE UPDATE ON interview_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_assessments_updated_at BEFORE UPDATE ON assessments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_coding_problems_updated_at BEFORE UPDATE ON coding_problems FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_mcq_questions_updated_at BEFORE UPDATE ON mcq_questions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
