from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from misskeycrawler.db.Base import Base
from misskeycrawler.db.Model import Note


class NoteDB(Base):
    def __init__(self, db_path: str = "mc_db.db"):
        super().__init__(db_path)

    def select(self):
        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()
        result = session.query(Note).all()
        session.close()
        return result

    def upsert(self, record: Note | list[Note] | list[dict]) -> list[int]:
        """upsert

        Args:
            record (Note | list[Note] | list[dict]): 投入レコード、またはレコード辞書のリスト

        Returns:
            list[int]: レコードに対応した投入結果のリスト
                       追加したレコードは0、更新したレコードは1が入る
        """
        result: list[int] = []
        record_list: list[Note] = []
        if isinstance(record, Note):
            record_list = [record]
        elif isinstance(record, list):
            if len(record) == 0:
                raise ValueError("record list is empty.")
            if isinstance(record[0], dict):
                record_list = [Note.create(r) for r in record]
            elif isinstance(record[0], Note):
                record_list = record
            else:
                raise ValueError("record list include invalid element.")

        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()

        for r in record_list:
            try:
                q = session.query(Note).filter(
                    and_(Note.note_id == r.note_id)
                ).with_for_update()
                p = q.one()
            except NoResultFound:
                # INSERT
                session.add(r)
                result.append(0)
            else:
                # UPDATE
                p.note_id = r.note_id
                p.user_id = r.user_id
                p.url = r.url
                p.text = r.text
                p.created_at = r.created_at
                p.registered_at = r.registered_at
                result.append(1)

        session.commit()
        session.close()
        return result