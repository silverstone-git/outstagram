--
-- PostgreSQL database dump
--

-- Dumped from database version 17.2
-- Dumped by pg_dump version 17.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: outsie; Type: SCHEMA; Schema: -; Owner: outstagrammer
--

CREATE SCHEMA outsie;


-- ALTER SCHEMA outsie OWNER TO outstagrammer;

--
-- Name: followrequest_status; Type: TYPE; Schema: outsie; Owner: outstagrammer
--

CREATE TYPE outsie.followrequest_status AS ENUM (
    'pending',
    'accepted',
    'rejected'
);


-- ALTER TYPE outsie.followrequest_status OWNER TO outstagrammer;

--
-- Name: post_post_category; Type: TYPE; Schema: outsie; Owner: outstagrammer
--

CREATE TYPE outsie.post_post_category AS ENUM (
    'tech',
    'entertainment',
    'business',
    'vlog',
    'lifestyle'
);


-- ALTER TYPE outsie.post_post_category OWNER TO outstagrammer;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: followrequest; Type: TABLE; Schema: outsie; Owner: outstagrammer
--

CREATE TABLE outsie.followrequest (
    request_id bigint NOT NULL,
    requester_user_id bigint NOT NULL,
    requested_user_id bigint NOT NULL,
    datetime_requested timestamp with time zone NOT NULL,
    status outsie.followrequest_status NOT NULL
);


-- ALTER TABLE outsie.followrequest OWNER TO outstagrammer;

--
-- Name: followrequest_request_id_seq; Type: SEQUENCE; Schema: outsie; Owner: outstagrammer
--

CREATE SEQUENCE outsie.followrequest_request_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- ALTER SEQUENCE outsie.followrequest_request_id_seq OWNER TO outstagrammer;

--
-- Name: followrequest_request_id_seq; Type: SEQUENCE OWNED BY; Schema: outsie; Owner: outstagrammer
--

ALTER SEQUENCE outsie.followrequest_request_id_seq OWNED BY outsie.followrequest.request_id;


--
-- Name: friendship; Type: TABLE; Schema: outsie; Owner: outstagrammer
--

CREATE TABLE outsie.friendship (
    user1_id bigint NOT NULL,
    user2_id bigint NOT NULL,
    datetime_friended timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    being_followed bigint
);


-- ALTER TABLE outsie.friendship OWNER TO outstagrammer;

--
-- Name: mediaurl; Type: TABLE; Schema: outsie; Owner: outstagrammer
--

CREATE TABLE outsie.mediaurl (
    post_id character varying(255) NOT NULL,
    url character varying(255) NOT NULL
);


-- ALTER TABLE outsie.mediaurl OWNER TO outstagrammer;

--
-- Name: post; Type: TABLE; Schema: outsie; Owner: outstagrammer
--

CREATE TABLE outsie.post (
    post_id character varying(255) NOT NULL,
    caption text,
    post_category outsie.post_post_category NOT NULL,
    datetime_posted timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    author_user_id bigint,
    highlighted_by_author boolean DEFAULT false
);


-- ALTER TABLE outsie.post OWNER TO outstagrammer;

--
-- Name: postcomment; Type: TABLE; Schema: outsie; Owner: outstagrammer
--

CREATE TABLE outsie.postcomment (
    comment_id bigint NOT NULL,
    post_id character varying(255) DEFAULT NULL::character varying,
    content character varying(255) NOT NULL,
    author_user_id bigint,
    datetime_commented timestamp with time zone NOT NULL
);


-- ALTER TABLE outsie.postcomment OWNER TO outstagrammer;

--
-- Name: postcomment_comment_id_seq; Type: SEQUENCE; Schema: outsie; Owner: outstagrammer
--

CREATE SEQUENCE outsie.postcomment_comment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- ALTER SEQUENCE outsie.postcomment_comment_id_seq OWNER TO outstagrammer;

--
-- Name: postcomment_comment_id_seq; Type: SEQUENCE OWNED BY; Schema: outsie; Owner: outstagrammer
--

ALTER SEQUENCE outsie.postcomment_comment_id_seq OWNED BY outsie.postcomment.comment_id;


--
-- Name: postcommentlike; Type: TABLE; Schema: outsie; Owner: outstagrammer
--

CREATE TABLE outsie.postcommentlike (
    comment_id bigint NOT NULL,
    liker_user_id bigint NOT NULL,
    datetime_liked timestamp with time zone NOT NULL
);


-- ALTER TABLE outsie.postcommentlike OWNER TO outstagrammer;

--
-- Name: postlike; Type: TABLE; Schema: outsie; Owner: outstagrammer
--

CREATE TABLE outsie.postlike (
    post_id character varying(255) NOT NULL,
    liker_user_id bigint NOT NULL,
    datetime_liked timestamp with time zone NOT NULL
);


-- ALTER TABLE outsie.postlike OWNER TO outstagrammer;

--
-- Name: user; Type: TABLE; Schema: outsie; Owner: outstagrammer
--

CREATE TABLE outsie."user" (
    user_id bigint NOT NULL,
    fullname character varying(255) NOT NULL,
    username character varying(100) NOT NULL,
    bio text,
    date_of_birth date,
    email character varying(255) NOT NULL,
    password character varying(255) NOT NULL
);


-- ALTER TABLE outsie."user" OWNER TO outstagrammer;

--
-- Name: user_user_id_seq; Type: SEQUENCE; Schema: outsie; Owner: outstagrammer
--

CREATE SEQUENCE outsie.user_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- ALTER SEQUENCE outsie.user_user_id_seq OWNER TO outstagrammer;

--
-- Name: user_user_id_seq; Type: SEQUENCE OWNED BY; Schema: outsie; Owner: outstagrammer
--

ALTER SEQUENCE outsie.user_user_id_seq OWNED BY outsie."user".user_id;


--
-- Name: followrequest request_id; Type: DEFAULT; Schema: outsie; Owner: outstagrammer
--

ALTER TABLE ONLY outsie.followrequest ALTER COLUMN request_id SET DEFAULT nextval('outsie.followrequest_request_id_seq'::regclass);


--
-- Name: postcomment comment_id; Type: DEFAULT; Schema: outsie; Owner: outstagrammer
--

ALTER TABLE ONLY outsie.postcomment ALTER COLUMN comment_id SET DEFAULT nextval('outsie.postcomment_comment_id_seq'::regclass);


--
-- Name: user user_id; Type: DEFAULT; Schema: outsie; Owner: outstagrammer
--

ALTER TABLE ONLY outsie."user" ALTER COLUMN user_id SET DEFAULT nextval('outsie.user_user_id_seq'::regclass);


SELECT pg_catalog.setval('outsie.followrequest_request_id_seq', 1, true);


--
-- Name: postcomment_comment_id_seq; Type: SEQUENCE SET; Schema: outsie; Owner: outstagrammer
--

SELECT pg_catalog.setval('outsie.postcomment_comment_id_seq', 1, true);


--
-- Name: user_user_id_seq; Type: SEQUENCE SET; Schema: outsie; Owner: outstagrammer
--

SELECT pg_catalog.setval('outsie.user_user_id_seq', 6, true);


--
-- Name: followrequest idx_16412_primary; Type: CONSTRAINT; Schema: outsie; Owner: outstagrammer
--

ALTER TABLE ONLY outsie.followrequest
    ADD CONSTRAINT idx_16412_primary PRIMARY KEY (request_id);


--
-- Name: friendship idx_16416_primary; Type: CONSTRAINT; Schema: outsie; Owner: outstagrammer
--

ALTER TABLE ONLY outsie.friendship
    ADD CONSTRAINT idx_16416_primary PRIMARY KEY (user1_id, user2_id);


--
-- Name: mediaurl idx_16420_primary; Type: CONSTRAINT; Schema: outsie; Owner: outstagrammer
--

ALTER TABLE ONLY outsie.mediaurl
    ADD CONSTRAINT idx_16420_primary PRIMARY KEY (post_id, url);


--
-- Name: post idx_16425_primary; Type: CONSTRAINT; Schema: outsie; Owner: outstagrammer
--

ALTER TABLE ONLY outsie.post
    ADD CONSTRAINT idx_16425_primary PRIMARY KEY (post_id);


--
-- Name: postcomment idx_16433_primary; Type: CONSTRAINT; Schema: outsie; Owner: outstagrammer
--

ALTER TABLE ONLY outsie.postcomment
    ADD CONSTRAINT idx_16433_primary PRIMARY KEY (comment_id);


--
-- Name: postcommentlike idx_16440_primary; Type: CONSTRAINT; Schema: outsie; Owner: outstagrammer
--

ALTER TABLE ONLY outsie.postcommentlike
    ADD CONSTRAINT idx_16440_primary PRIMARY KEY (comment_id, liker_user_id);


--
-- Name: postlike idx_16443_primary; Type: CONSTRAINT; Schema: outsie; Owner: outstagrammer
--

ALTER TABLE ONLY outsie.postlike
    ADD CONSTRAINT idx_16443_primary PRIMARY KEY (post_id, liker_user_id);


--
-- Name: user idx_16447_primary; Type: CONSTRAINT; Schema: outsie; Owner: outstagrammer
--

ALTER TABLE ONLY outsie."user"
    ADD CONSTRAINT idx_16447_primary PRIMARY KEY (user_id);


--
-- Name: idx_16412_requested_user_id; Type: INDEX; Schema: outsie; Owner: outstagrammer
--

CREATE INDEX idx_16412_requested_user_id ON outsie.followrequest USING btree (requested_user_id);


--
-- Name: idx_16412_requester_user_id; Type: INDEX; Schema: outsie; Owner: outstagrammer
--

CREATE INDEX idx_16412_requester_user_id ON outsie.followrequest USING btree (requester_user_id);


--
-- Name: idx_16416_user1_id; Type: INDEX; Schema: outsie; Owner: outstagrammer
--

CREATE UNIQUE INDEX idx_16416_user1_id ON outsie.friendship USING btree (user1_id, user2_id);


--
-- Name: idx_16416_user2_id; Type: INDEX; Schema: outsie; Owner: outstagrammer
--

CREATE INDEX idx_16416_user2_id ON outsie.friendship USING btree (user2_id);


--
-- Name: idx_16425_author_user_id; Type: INDEX; Schema: outsie; Owner: outstagrammer
--

CREATE INDEX idx_16425_author_user_id ON outsie.post USING btree (author_user_id);


--
-- Name: idx_16433_author_user_id; Type: INDEX; Schema: outsie; Owner: outstagrammer
--

CREATE INDEX idx_16433_author_user_id ON outsie.postcomment USING btree (author_user_id);


--
-- Name: idx_16433_post_id; Type: INDEX; Schema: outsie; Owner: outstagrammer
--

CREATE INDEX idx_16433_post_id ON outsie.postcomment USING btree (post_id);


--
-- Name: idx_16440_liker_user_id; Type: INDEX; Schema: outsie; Owner: outstagrammer
--

CREATE INDEX idx_16440_liker_user_id ON outsie.postcommentlike USING btree (liker_user_id);


--
-- Name: idx_16443_liker_user_id; Type: INDEX; Schema: outsie; Owner: outstagrammer
--

CREATE INDEX idx_16443_liker_user_id ON outsie.postlike USING btree (liker_user_id);


--
-- Name: idx_16447_email; Type: INDEX; Schema: outsie; Owner: outstagrammer
--

CREATE UNIQUE INDEX idx_16447_email ON outsie."user" USING btree (email);


--
-- Name: idx_16447_username; Type: INDEX; Schema: outsie; Owner: outstagrammer
--

CREATE UNIQUE INDEX idx_16447_username ON outsie."user" USING btree (username);


--
-- Name: followrequest followrequest_ibfk_1; Type: FK CONSTRAINT; Schema: outsie; Owner: outstagrammer
--

ALTER TABLE ONLY outsie.followrequest
    ADD CONSTRAINT followrequest_ibfk_1 FOREIGN KEY (requester_user_id) REFERENCES outsie."user"(user_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: followrequest followrequest_ibfk_2; Type: FK CONSTRAINT; Schema: outsie; Owner: outstagrammer
--

ALTER TABLE ONLY outsie.followrequest
    ADD CONSTRAINT followrequest_ibfk_2 FOREIGN KEY (requested_user_id) REFERENCES outsie."user"(user_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: friendship friendship_ibfk_1; Type: FK CONSTRAINT; Schema: outsie; Owner: outstagrammer
--

ALTER TABLE ONLY outsie.friendship
    ADD CONSTRAINT friendship_ibfk_1 FOREIGN KEY (user1_id) REFERENCES outsie."user"(user_id) ON UPDATE RESTRICT ON DELETE CASCADE;


--
-- Name: friendship friendship_ibfk_2; Type: FK CONSTRAINT; Schema: outsie; Owner: outstagrammer
--

ALTER TABLE ONLY outsie.friendship
    ADD CONSTRAINT friendship_ibfk_2 FOREIGN KEY (user2_id) REFERENCES outsie."user"(user_id) ON UPDATE RESTRICT ON DELETE CASCADE;


--
-- Name: mediaurl mediaurl_ibfk_1; Type: FK CONSTRAINT; Schema: outsie; Owner: outstagrammer
--

ALTER TABLE ONLY outsie.mediaurl
    ADD CONSTRAINT mediaurl_ibfk_1 FOREIGN KEY (post_id) REFERENCES outsie.post(post_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: post post_ibfk_1; Type: FK CONSTRAINT; Schema: outsie; Owner: outstagrammer
--

ALTER TABLE ONLY outsie.post
    ADD CONSTRAINT post_ibfk_1 FOREIGN KEY (author_user_id) REFERENCES outsie."user"(user_id) ON UPDATE RESTRICT ON DELETE CASCADE;


--
-- Name: postcomment postcomment_ibfk_1; Type: FK CONSTRAINT; Schema: outsie; Owner: outstagrammer
--

ALTER TABLE ONLY outsie.postcomment
    ADD CONSTRAINT postcomment_ibfk_1 FOREIGN KEY (post_id) REFERENCES outsie.post(post_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: postcomment postcomment_ibfk_2; Type: FK CONSTRAINT; Schema: outsie; Owner: outstagrammer
--

ALTER TABLE ONLY outsie.postcomment
    ADD CONSTRAINT postcomment_ibfk_2 FOREIGN KEY (author_user_id) REFERENCES outsie."user"(user_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: postcommentlike postcommentlike_ibfk_1; Type: FK CONSTRAINT; Schema: outsie; Owner: outstagrammer
--

ALTER TABLE ONLY outsie.postcommentlike
    ADD CONSTRAINT postcommentlike_ibfk_1 FOREIGN KEY (comment_id) REFERENCES outsie.postcomment(comment_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: postcommentlike postcommentlike_ibfk_2; Type: FK CONSTRAINT; Schema: outsie; Owner: outstagrammer
--

ALTER TABLE ONLY outsie.postcommentlike
    ADD CONSTRAINT postcommentlike_ibfk_2 FOREIGN KEY (liker_user_id) REFERENCES outsie."user"(user_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: postlike postlike_ibfk_2; Type: FK CONSTRAINT; Schema: outsie; Owner: outstagrammer
--

ALTER TABLE ONLY outsie.postlike
    ADD CONSTRAINT postlike_ibfk_2 FOREIGN KEY (liker_user_id) REFERENCES outsie."user"(user_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- PostgreSQL database dump complete
--

