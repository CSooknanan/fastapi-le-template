import typer
from app.database import create_db_and_tables, get_cli_session, drop_all
from app.models import *
from fastapi import Depends
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from app.utilities import encrypt_password

cli = typer.Typer()

@cli.command()
def initialize():
    with get_cli_session() as db:
        drop_all() 
        create_db_and_tables() 
        
        bob = UserBase(username='bob', email='bob@mail.com', password=encrypt_password("bobpass"))
        bob_db = User.model_validate(bob)

        db.add(bob_db)
        db.commit()


        album1= Album(
            title="THY WILL BE DONE",
            artist="$uicideboy$",
            image_url="https://weblabs.web.app/api/brainrot/1.webp "
        )
        db.add(album1)
        db.commit()

        track1 = Track(
            title="Kill Yourself Part III",
            duration="3:45",
            album_id=album1.id
        )
        db.add(track1)
        db.commit()

        comment1= Comment(
            text="Great track!",
            track_id=track1.id
        )
        db.add(comment1)
        db.commit()

        # New World Depression
        album2 = Album(
            title="New World Depression",
            artist="$uicideboy$",
            image_url="https://weblabs.web.app/api/brainrot/2.webp"
        )
        db.add(album2)
        db.commit()

        track2 = Track(
            title="Champagne Face",
            duration="3:30",
            album_id=album2.id
        )
        db.add(track2)
        db.commit()

        track3 = Track(
            title="New World Depression",
            duration="3:45",
            album_id=album2.id
        )
        db.add(track3)
        db.commit()

        track4 = Track(
            title="Fuck The Industry",
            duration="4:00",
            album_id=album2.id
        )
        db.add(track4)
        db.commit()

        comment2 = Comment(
            text="This album hits different!",
            track_id=track2.id
        )
        db.add(comment2)
        db.commit()

        comment3 = Comment(
            text="Dark and intense vibes.",
            track_id=track3.id
        )
        db.add(comment3)
        db.commit()

        # Long Term Effects of Suffering
        album3 = Album(
            title="Long Term Effects of Suffering",
            artist="$uicideboy$",
            image_url="https://weblabs.web.app/api/brainrot/1.webp"
        )
        db.add(album3)
        db.commit()

        track5 = Track(
            title="King Tulip",
            duration="3:20",
            album_id=album3.id
        )
        db.add(track5)
        db.commit()

        track6 = Track(
            title="Bring Out Your Dead",
            duration="3:50",
            album_id=album3.id
        )
        db.add(track6)
        db.commit()

        track7 = Track(
            title="Pierrot Le Fou",
            duration="4:10",
            album_id=album3.id
        )
        db.add(track7)
        db.commit()

        comment4 = Comment(
            text="Classic $uicideboy$ track!",
            track_id=track5.id
        )
        db.add(comment4)
        db.commit()

        comment5 = Comment(
            text="The lyrics are so raw.",
            track_id=track6.id
        )
        db.add(comment5)
        db.commit()

        comment6 = Comment(
            text="This one gives me chills.",
            track_id=track7.id
        )
        db.add(comment6)
        db.commit()


        print("Database Initialized")

@cli.command()
def test():
    print("You're already in the test")


if __name__ == "__main__":
    cli()