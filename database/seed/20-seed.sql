-- voices
INSERT INTO voices (id, user_id, name, provider, voice_id, language, gender, settings, is_public, is_active)
SELECT gen_random_uuid(), NULL, '日本語女性1', 'google_tts', 'ja-JP-Neural2-F', 'ja', 'female', '{"speed":1.0,"pitch":0.0}', true, true
WHERE NOT EXISTS (SELECT 1 FROM voices WHERE provider='google_tts' AND voice_id='ja-JP-Neural2-F');

INSERT INTO voices (id, user_id, name, provider, voice_id, language, gender, settings, is_public, is_active)
SELECT gen_random_uuid(), NULL, '日本語男性1', 'google_tts', 'ja-JP-Neural2-D', 'ja', 'male', '{"speed":1.0,"pitch":0.0}', true, true
WHERE NOT EXISTS (SELECT 1 FROM voices WHERE provider='google_tts' AND voice_id='ja-JP-Neural2-D');

INSERT INTO voices (id, user_id, name, provider, voice_id, language, gender, settings, is_public, is_active)
SELECT gen_random_uuid(), NULL, '英語女性1', 'google_tts', 'en-US-Neural2-F', 'en', 'female', '{"speed":1.0,"pitch":0.0}', true, true
WHERE NOT EXISTS (SELECT 1 FROM voices WHERE provider='google_tts' AND voice_id='en-US-Neural2-F');

INSERT INTO voices (id, user_id, name, provider, voice_id, language, gender, settings, is_public, is_active)
SELECT gen_random_uuid(), NULL, '英語男性1', 'google_tts', 'en-US-Neural2-D', 'en', 'male', '{"speed":1.0,"pitch":0.0}', true, true
WHERE NOT EXISTS (SELECT 1 FROM voices WHERE provider='google_tts' AND voice_id='en-US-Neural2-D');

-- personality_templates
INSERT INTO personality_templates (id, user_id, name, description, personality_type, system_prompt, characteristics, is_public, is_active)
SELECT gen_random_uuid(), NULL, 'プロフェッショナル', 'ビジネス向けの専門的で丁寧な性格', 'professional',
       'あなたは専門的で丁寧なビジネスアシスタントです。常に正確で簡潔な回答を心がけてください。',
       '{"formality":"high","detail_level":"medium","tone":"professional"}', true, true
WHERE NOT EXISTS (SELECT 1 FROM personality_templates WHERE user_id IS NULL AND name='プロフェッショナル');

INSERT INTO personality_templates (id, user_id, name, description, personality_type, system_prompt, characteristics, is_public, is_active)
SELECT gen_random_uuid(), NULL, 'フレンドリー', '親しみやすく気さくな性格', 'friendly',
       'あなたは親しみやすく気さくなアシスタントです。ユーザーと自然な会話を楽しみながらサポートします。',
       '{"formality":"low","detail_level":"medium","tone":"friendly"}', true, true
WHERE NOT EXISTS (SELECT 1 FROM personality_templates WHERE user_id IS NULL AND name='フレンドリー');

INSERT INTO personality_templates (id, user_id, name, description, personality_type, system_prompt, characteristics, is_public, is_active)
SELECT gen_random_uuid(), NULL, 'クリエイティブ', '創造的で独創的なアイデアを提供する性格', 'creative',
       'あなたは創造的で独創的なアシスタントです。新しい視点や革新的なアイデアを提供します。',
       '{"formality":"medium","detail_level":"high","tone":"creative"}', true, true
WHERE NOT EXISTS (SELECT 1 FROM personality_templates WHERE user_id IS NULL AND name='クリエイティブ');

INSERT INTO personality_templates (id, user_id, name, description, personality_type, system_prompt, characteristics, is_public, is_active)
SELECT gen_random_uuid(), NULL, 'アナリティカル', '論理的で分析的な性格', 'analytical',
       'あなたは論理的で分析的なアシスタントです。データに基づいた客観的な分析を提供します。',
       '{"formality":"high","detail_level":"high","tone":"analytical"}', true, true
WHERE NOT EXISTS (SELECT 1 FROM personality_templates WHERE user_id IS NULL AND name='アナリティカル');
