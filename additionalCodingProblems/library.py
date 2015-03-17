"""Programming assignment for ACT.md software engineering position.

Your task is to implement the Library system below to the specification
provided in the documentation string. If the documentation is in any
way ambiguous, please email Patrick Schmid (prschmid@act.md) for clarification.
If you feel that auxiliary helper functions/classes would be helpful, feel free
to write them. You may change anything in this file except you are not
permitted to alter Library API or the fact that a Book requires an ISBN and
a user an email address.

Although we provide you with some test cases, do not assume that these cover
all corner cases, and we may use a different set of inputs to validate your
solution. We will be looking at your solution both for correctness and for
style.

Best of luck!
"""

# =============================================================================
#
# Implement the things below
#
# =============================================================================

import sqlite3


class Book(object):
    """A book in the library.

    You can also assume that the ISBN number is the unique identifier for a
    book. However, if a book with the same ISBN gets added with a different
    title, you can assume that this is an error case.
    """

    def __init__(self, isbn, title):
        self.isbn = isbn
        self.title = title


class User(object):
    """A user of the library."""

    def __init__(self, email, first_name, last_name):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name


LIBRARY_DB_NAME = 'library.db'


class Library(object):
    """A library of books and users.

    This is a (simplistic) library of books and users where we can add books
    and users, and allow users to checkout those books. As this library exists
    in the land of Utopia, there are no due dates for books being checked out.
    However, we're not going to let this be a free-for-all, and so a user can
    only checkout a total of MAX_LOANS_PER_USER books at a time.
    """

    MAX_LOANS_PER_USER = 5
    """The maximum  number of loans per user."""

    def __init__(self):
        """Initialize the library."""
        self.conn = sqlite3.connect(LIBRARY_DB_NAME)

        cursor = self.conn.cursor()

        # drop all tables
        cursor.execute("DROP TABLE IF EXISTS USERS")
        cursor.execute("DROP TABLE IF EXISTS BOOKS")
        cursor.execute("DROP TABLE IF EXISTS USER_LOANS")

        cursor.execute('CREATE TABLE USERS (email text, first_name text, last_name text, PRIMARY KEY (email))')
        cursor.execute('CREATE TABLE BOOKS '
                       '(isbn text, title text, number_of_copies integer, number_of_copies_left integer, '
                       'PRIMARY KEY (isbn))')

        cursor.execute('CREATE TABLE USER_LOANS (email text, isbn text, FOREIGN KEY(email) REFERENCES USERS(email),'
                       'FOREIGN KEY(isbn) REFERENCES BOOKS(isbn))')

        self.conn.commit()
        # no need to close connection - will be reused

    def add_book(self, book):
        """Add a new book to the library.

        If there is already an book with the same ISBN number, then this should
        update the number of copies of that book available in the library.

        Args:
            book: The new book to add to the library.
        Returns:
            The number of copies of the book that exist in the library after
            this new book was added.
        Raises:
            ValueError: If the book is None.
        """
        if book is None:
            raise ValueError

        result = 0

        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM BOOKS WHERE isbn=?', (book.isbn,))
        row = cursor.fetchone()
        if row is not None:
            if book.title == row[1]:
                cursor.execute('UPDATE BOOKS SET number_of_copies_left = number_of_copies_left + 1 WHERE isbn =?',
                               (book.isbn,))
                cursor.execute('UPDATE BOOKS SET number_of_copies = number_of_copies + 1 WHERE isbn =?',
                               (book.isbn,))
                result = row[2] + 1
        else:
            cursor.execute('INSERT INTO BOOKS values (?,?,?,?)',
                           (book.isbn, book.title, 1, 1))
            result = 1

        self.conn.commit()
        return result

    def get_books(self):
        """Get a list of all books.

        If the book has multiple copies in the library, it should only be in
        this list once. I.e. even if we have 10 copies of "Catcher in the Rye"
        it should only be in this list once.

        Returns:
            A list of all books. There is no ordering guarantee.
        """
        all_books = []
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM BOOKS')

        all_rows = cursor.fetchall()

        # assuming the list can fit in memory
        for row in all_rows:
            all_books.append(Book(row[0], row[1]))

        return all_books

    def get_book(self, isbn):
        """Get a book with the given ISBN number.

        Args:
            isbn: The ISBN number of the book to get.
        Returns:
            The book corresponding to that ISBN number or None if no such book
            exists.
        Raises:
            ValueError: If the isbn is None.
        """
        if isbn is None:
            raise ValueError

        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM BOOKS WHERE isbn=?', (isbn,))

        row = cursor.fetchall()
        if len(row) == 0:
            return None

        return Book(row[0], row[1])

    def get_number_of_books(self, unique=True):
        """Get an number of total books in the library.

        For example if our library only contains 2 copies of "Moby Dick" then
        if unique=True, this should return 1. If unique is False, it should
        return 2.

        Args:
            unique: A flag to set whether or not we want the total number of
                unique books, or the total number of books (i.e. all copies)
        Returns:
            The number of total books in the library.
        """
        cursor = self.conn.cursor()
        if unique:
            cursor.execute('SELECT count(*) FROM BOOKS')
        else:
            cursor.execute('SELECT SUM(number_of_copies) FROM BOOKS')

        return cursor.fetchone()[0]

    def get_number_of_copies(self, isbn):
        """Get an number of total copies of book with the given ISBN number.

        Args:
            isbn: The ISBN number of the book to get.
        Returns:
            The number of total copies in the library for the given book
            regardless of how many have been checked out.
        Raises:
            ValueError: If the isbn is None.
        """
        if isbn is None:
            raise ValueError

        cursor = self.conn.cursor()
        cursor.execute('SELECT number_of_copies FROM BOOKS WHERE isbn=?', (isbn,))

        return cursor.fetchone()[0]

    def get_number_of_available_copies(self, isbn):
        """Get an number of available copies of book with the given ISBN
        number.

        Args:
            isbn: The ISBN number of the book to get.
        Returns:
            The number of available copies in the library that can be checked
            out by users.
        Raises:
            ValueError: If the isbn is None.
        """
        if isbn is None:
            raise ValueError

        cursor = self.conn.cursor()
        cursor.execute('SELECT number_of_copies_left FROM BOOKS WHERE isbn=?', (isbn,))

        row = cursor.fetchone()
        if row is None:
            return 0
        else:
            return row[0]

    def search_books_by_title(self, title):
        """Search all books by title.

        This should be a case insensitive partial match such that if there is a
        book called "To Kill A Mockingbird" then "ill", "ingb", and "ll a m"
        should all be valid matches.

        If the book has multiple copies in the library, it should only be in
        this list once. I.e. even if we have 10 copies of "Catcher in the Rye"
        it should only be in this list once.

        Args:
            title: The title string to search for.
        Returns:
            A list of books objects that match the search criteria.
        Raises:
            ValueError: If the title is None.
        """
        if title is None:
            raise ValueError

        books = []
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM BOOKS WHERE title LIKE \'%%%s%%\'' % title)

        all_rows = cursor.fetchall()

        # assuming the list can fit in memory
        for row in all_rows:
            books.append(Book(row[0], row[1]))

        return books

    def add_user(self, user):
        """Add a new user to the library system.

        Args:
            user: The user to add
        Returns:
            True if everything succeeded, else False.
        Raises:
            ValueError: If the user is None.
            ValueError: Is raised if there is already a user with the same
                email address. Email addresses are case insensitive so
                "john@doe.com" and "John@Doe.com" are considered to be the
                same.
        """
        if user is None:
            raise ValueError

        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM USERS WHERE email=?', (user.email.lower(),))

        row = cursor.fetchone()
        if row is not None:
            if user.email.lower() == row[0].lower():
                raise ValueError
        else:
            cursor.execute('INSERT INTO USERS values (?,?,?)',
                           (user.email.lower(), user.first_name, user.last_name))

        self.conn.commit()
        return True

    def get_users(self):
        """Get a list of all users.

        Returns:
            A list of all users. There is no ordering guarantee.
        """
        all_users = []
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users')

        all_rows = cursor.fetchall()

        # assuming the list can fit in memory
        for row in all_rows:
            all_users.append(User(row[0], row[1], row[2]))

        return all_users

    def get_user_by_email(self, email):
        """Get the user with the given email.

        This should be a case insensitive but it requires the the email to
        match completely. I.e. there is user with the email address
        "super@man.com", then "Super@Man.com", "super@man.Com", and
        "super@man.com" should all be valid matches.

        Args:
            email: The email string to search for.
        Returns:
            The user with the given email address or None, if that user does
            not exist.
        Raises:
            ValueError: If the email is None.
        """
        if email is None:
            raise ValueError

        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM USERS WHERE email=?', (email.lower(),))

        row = cursor.fetchone()
        if row is None:
            return row
        return User(row[0], row[1], row[2])

    def search_users_by_email(self, email):
        """Search all users by email.

        This should be a case insensitive partial match such that if there is
        an email named "superman@marvel.com", then "uper", "man@ma", "vel.co"
        should all be valid matches.

        Args:
            email: The email string to search for.
        Returns:
            A list of users objects that match the search criteria.
        Raises:
            ValueError: If the email is None.
        """
        if email is None:
            raise ValueError

        users = []
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM USERS WHERE email LIKE \'%%%s%%\'' % email.lower())

        all_rows = cursor.fetchall()

        # assuming the list can fit in memory
        for row in all_rows:
            users.append(User(row[0], row[1], row[2]))

        return users

    def validate_book(self, book):
        cursor = self.conn.cursor()
        cursor.execute('SELECT count(*) FROM BOOKS WHERE isbn=?', (book.isbn,))
        row = cursor.fetchone()[0]
        if row == 0:
            raise KeyError

    def validate_user(self, user):
        cursor = self.conn.cursor()
        cursor.execute('SELECT count(*) FROM USERS WHERE email=?', (user.email.lower(),))
        row = cursor.fetchone()[0]
        if row == 0:
            raise KeyError

    def checkout_book(self, user, book):
        """Allow the user to checkout an book.

        If the user already has the maximum number of books, this will return
        False, as (s)he is not allowed to checkout another book.

        Also, if the user already has a copy of this book checked out, then
        this will return False.

        Args:
            user: The user object trying to checkout the book.
            book: The book object the user is trying to checkout.
        Returns:
            True if the book was successfully checked out, else False.
        Raises:
            ValueError: If the user or book are None.
            KeyError: If the user is not a valid user in the library.
            KeyError: If the book is not a valid book in the library.

        """
        if user is None:
            raise ValueError
        if book is None:
            raise ValueError

        self.validate_book(book)

        user_checkouts = self.get_checkouts_for_user(user)
        if len(user_checkouts) == self.MAX_LOANS_PER_USER:
            return False
        else:
            for checkout in user_checkouts:
                if checkout.isbn == book.isbn:
                    return False

        if self.get_number_of_available_copies(book.isbn) == 0:
            return False

        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO USER_LOANS values (?,?)',
                       (user.email.lower(), book.isbn))

        cursor.execute('UPDATE BOOKS SET number_of_copies_left = number_of_copies_left - 1 WHERE isbn =?',
                       (book.isbn,))
        self.conn.commit()
        return True

    def return_book(self, user, book):
        """Allow the user to return an book.

        Args:
            user: The user object trying to return the book.
            book: The book object the user is trying to return.
        Returns:
            True if the book was successfully returned out, else False.
        Raises:
            ValueError: If the user or book are None.
            ValueError: If the user has not checked out this book.
            KeyError: If the user is not a valid user in the library.
            KeyError: If the book is not a valid book in the library.
        """
        if user is None:
            raise ValueError
        if book is None:
            raise ValueError

        self.validate_book(book)
        self.validate_user(user)

        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM USER_LOANS WHERE email=? AND isbn =?', (user.email, book.isbn))

        cursor.execute('UPDATE BOOKS SET number_of_copies_left = number_of_copies_left + 1 WHERE isbn =?',
                       (book.isbn,))
        self.conn.commit()
        return True

    def get_checkouts_for_user(self, user):
        """Get all of the outstanding loans for a user.

        Args:
            user: The user object we are querying for.
        Returns:
            A list of Books that the user has checked out.
        Raises:
            ValueError: If the user is None.
            KeyError: If the user is not a valid user in the library.
        """
        if user is None:
            raise ValueError

        books = []

        self.validate_user(user)
        cursor = self.conn.cursor()
        cursor.execute('SELECT BOOKS.isbn, title FROM BOOKS, USER_LOANS WHERE email=? AND BOOKS.isbn=USER_LOANS.isbn',
                       (user.email,))

        all_rows = cursor.fetchall()

        for row in all_rows:
            books.append(Book(row[0], row[1]))

        return books


# =============================================================================
#
# A simple main function for you to run. You should be able to test your
# implementation by simply running this module. E.g.
# python library.py
#
# =============================================================================

if __name__ == '__main__':
    """The main entry point for this module.

    The main entry point for the function that runs a couple tests to validate
    the implementation of your Library.

    If you feel like creating a unittest.TestCase for all of this, feel free
    to do so (we will, when testing your implementation)
    """

    library = Library()

    # Add some books to the library (As you can see, we not using real ISBN
    # numbers... there is no need for you to make sure that they are real.)
    library.add_book(Book('12345', u"Catcher in the Rye"))
    print library.get_number_of_books(unique=True)
    assert library.get_number_of_books(unique=True) == 1, "Oops!"
    assert library.get_number_of_books(unique=False) == 1, "Oops!"
    assert library.get_number_of_copies('12345') == 1, "Oops!"

    library.add_book(Book('12345', u"Catcher in the Rye"))
    assert library.get_number_of_books(unique=True) == 1, "Oops!"
    assert library.get_number_of_books(unique=False) == 2, "Oops!"
    assert library.get_number_of_copies('12345') == 2, "Oops!"

    library.add_book(Book('12345', u"Catcher in the Rye"))
    assert library.get_number_of_books(unique=True) == 1, "Oops!"
    assert library.get_number_of_books(unique=False) == 3, "Oops!"
    assert library.get_number_of_copies('12345') == 3, "Oops!"

    library.add_book(Book('23456', u"Moby Dick"))
    library.add_book(Book('23456', u"Moby Dick"))

    library.add_book(Book('34567', u"To Kill A Mockingbird"))

    assert library.get_book('9999') is None, "Oops!"

    # The following should not be allowed
    # it doesn't change the state - since the book with this isbn already exists, it fails quietly. Not specified what
    # should have happened, decided on this approach.
    library.add_book(Book('34567', u"Different title"))

    assert library.get_number_of_books(unique=True) == 3, "Oops!"
    assert library.get_number_of_books(unique=False) == 6, "Oops!"
    assert library.get_number_of_copies('23456') == 2, "Oops!"
    assert library.get_number_of_copies('34567') == 1, "Oops!"

    # Add some users
    library.add_user(User(u"john@doe.com", u"John", u"Doe"))
    library.add_user(User(u"susan@doe.com", u"Susan", u"Doe"))
    assert len(library.get_users()) == 2, "Oops!"

    try:
        library.add_user(User(u"John@Doe.com", u"John", u"Doe"))
    except ValueError:
        pass
    else:
        raise RuntimeError("Oops!")

    assert library.get_user_by_email("haha@gmail.com") is None

    # Search for a book and user
    mockingbird = library.search_books_by_title("Mockingbird")[0]
    susan = library.search_users_by_email("susan")[0]

    assert mockingbird.isbn == '34567', "Oops!"
    assert susan.email == u"susan@doe.com", "Oops!"

    # Checkout a book
    library.checkout_book(susan, mockingbird)

    try:
        library.checkout_book(User('haha@gmail.com', 'tt', 'tts'), mockingbird)
    except KeyError:
        pass
    else:
        raise RuntimeError("Oops!")

    try:
        library.checkout_book(susan, Book(314159, "a"))
    except KeyError:
        pass
    else:
        raise RuntimeError("Oops!")

    assert len(library.get_checkouts_for_user(susan)) == 1, "Oops!"
    assert library.get_number_of_available_copies(mockingbird.isbn) == 0, "Oops!"

    # Can't check it out twice!
    assert library.checkout_book(susan, mockingbird) is False, "Oops!"

    # Get a user by email
    john = library.get_user_by_email(u"john@doe.com")

    # Try to checkout the book that is not available
    assert library.checkout_book(john, mockingbird) is False, "Oops!"
    assert len(library.get_checkouts_for_user(john)) == 0, "Oops!"

    # Return the book
    library.return_book(susan, mockingbird)
    assert library.get_number_of_available_copies(mockingbird.isbn) == 1, "Oops!"
    assert library.get_number_of_available_copies(12341341) == 0, "Oops"

    assert library.checkout_book(john, mockingbird) is True, "Oops!"
    assert len(library.get_checkouts_for_user(john)) == 1, "Oops!"

    assert library.get_number_of_available_copies(mockingbird.isbn) == 0, "Oops!"
