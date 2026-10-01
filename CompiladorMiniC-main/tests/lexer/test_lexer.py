"""Pruebas del analizador léxico de Mini C según SKILL.md."""

from minic.diagnostics.diagnostic import Diagnostic
from minic.lexer import Lexer, Token, TokenType
from minic.output import format_diagnostic, format_token


def test_empty_source() -> None:
    tokens, diagnostics = Lexer("").scan()
    assert diagnostics == []
    assert tokens == [Token(TokenType.EOF, "", None, 1, 1)]


def test_keywords_and_identifiers() -> None:
    source = "int while int2 whilex _ident id_123"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []

    types = [t.type for t in tokens]
    lexemes = [t.lexeme for t in tokens]

    assert types == [
        TokenType.KW_INT,
        TokenType.KW_WHILE,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.EOF,
    ]
    assert lexemes == ["int", "while", "int2", "whilex", "_ident", "id_123", ""]


def test_integer_literals() -> None:
    source = "0 42 007"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []

    assert [(t.lexeme, t.literal) for t in tokens[:-1]] == [
        ("0", 0),
        ("42", 42),
        ("007", 7),
    ]


def test_operators_and_symbols() -> None:
    source = "= + - == != ( ) { } ;"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []

    expected_types = [
        TokenType.ASSIGN,
        TokenType.PLUS,
        TokenType.MINUS,
        TokenType.EQUAL_EQUAL,
        TokenType.NOT_EQUAL,
        TokenType.LPAREN,
        TokenType.RPAREN,
        TokenType.LBRACE,
        TokenType.RBRACE,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]
    assert [t.type for t in tokens] == expected_types


def test_number_followed_by_identifier() -> None:
    source = "12abc"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []

    assert [(t.type, t.lexeme) for t in tokens[:-1]] == [
        (TokenType.INTEGER_LITERAL, "12"),
        (TokenType.IDENTIFIER, "abc"),
    ]


def test_negative_number_separated() -> None:
    source = "-5"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []

    assert [(t.type, t.lexeme, t.literal) for t in tokens[:-1]] == [
        (TokenType.MINUS, "-", None),
        (TokenType.INTEGER_LITERAL, "5", 5),
    ]


def test_positions_and_newlines() -> None:
    source = "int a;\nwhile (a == 1) {\n\ta = a + 1;\n}"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []

    # Check some key positions
    # Line 1: int a;
    assert tokens[0] == Token(TokenType.KW_INT, "int", None, 1, 1)
    assert tokens[1] == Token(TokenType.IDENTIFIER, "a", None, 1, 5)
    assert tokens[2] == Token(TokenType.SEMICOLON, ";", None, 1, 6)

    # Line 2: while (a == 1) {
    assert tokens[3] == Token(TokenType.KW_WHILE, "while", None, 2, 1)
    assert tokens[4] == Token(TokenType.LPAREN, "(", None, 2, 7)
    assert tokens[5] == Token(TokenType.IDENTIFIER, "a", None, 2, 8)
    assert tokens[6] == Token(TokenType.EQUAL_EQUAL, "==", None, 2, 10)
    assert tokens[7] == Token(TokenType.INTEGER_LITERAL, "1", 1, 2, 13)
    assert tokens[8] == Token(TokenType.RPAREN, ")", None, 2, 14)
    assert tokens[9] == Token(TokenType.LBRACE, "{", None, 2, 16)

    # Line 3: \ta = a + 1; (tab counts as 1 column)
    assert tokens[10] == Token(TokenType.IDENTIFIER, "a", None, 3, 2)
    assert tokens[11] == Token(TokenType.ASSIGN, "=", None, 3, 4)
    assert tokens[12] == Token(TokenType.IDENTIFIER, "a", None, 3, 6)
    assert tokens[13] == Token(TokenType.PLUS, "+", None, 3, 8)
    assert tokens[14] == Token(TokenType.INTEGER_LITERAL, "1", 1, 3, 10)
    assert tokens[15] == Token(TokenType.SEMICOLON, ";", None, 3, 11)

    # Line 4: }
    assert tokens[16] == Token(TokenType.RBRACE, "}", None, 4, 1)
    assert tokens[17] == Token(TokenType.EOF, "", None, 4, 2)


def test_skill_section7_case1() -> None:
    source = "int2 = 12abc;\nwhilex == -5"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []

    formatted_tokens = [format_token(t) for t in tokens]
    expected = [
        "IDENTIFIER 'int2' 1 1",
        "ASSIGN '=' 1 6",
        "INTEGER_LITERAL '12' 1 8",
        "IDENTIFIER 'abc' 1 10",
        "SEMICOLON ';' 1 13",
        "IDENTIFIER 'whilex' 2 1",
        "EQUAL_EQUAL '==' 2 8",
        "MINUS '-' 2 11",
        "INTEGER_LITERAL '5' 2 12",
        "EOF '' 2 13",
    ]
    assert formatted_tokens == expected


def test_skill_section7_case2_with_errors() -> None:
    source = "int x = @;\nx ! = 0; // fin"
    tokens, diagnostics = Lexer(source).scan()

    formatted_tokens = [format_token(t) for t in tokens]
    expected_tokens = [
        "KW_INT 'int' 1 1",
        "IDENTIFIER 'x' 1 5",
        "ASSIGN '=' 1 7",
        "SEMICOLON ';' 1 10",
        "IDENTIFIER 'x' 2 1",
        "ASSIGN '=' 2 5",
        "INTEGER_LITERAL '0' 2 7",
        "SEMICOLON ';' 2 8",
        "IDENTIFIER 'fin' 2 13",
        "EOF '' 2 16",
    ]
    assert formatted_tokens == expected_tokens

    formatted_diagnostics = [format_diagnostic(d) for d in diagnostics]
    expected_diagnostics = [
        "LEX001 error 1:9 Carácter no reconocido: '@'",
        "LEX001 error 2:3 Carácter no reconocido: '!'",
        "LEX001 error 2:10 Carácter no reconocido: '/'",
        "LEX001 error 2:11 Carácter no reconocido: '/'",
    ]
    assert formatted_diagnostics == expected_diagnostics
