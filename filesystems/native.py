import io
import os
import tempfile

from filesystems import Path, common, exceptions


_CREATE_FLAGS = os.O_EXCL | os.O_CREAT | os.O_RDWR | getattr(os, "O_BINARY", 0)


def _create_file(fs, path):
    try:
        fd = os.open(str(path), _CREATE_FLAGS)
    except (IOError, OSError) as error:
        if error.errno == exceptions.FileNotFound.errno:
            raise exceptions.FileNotFound(path)
        elif error.errno == exceptions.FileExists.errno:
            raise exceptions.FileExists(path)
        elif error.errno == exceptions.SymbolicLoop.errno:
            raise exceptions.SymbolicLoop(path.parent())
        raise

    return io.open(fd, "w+b")


def _open_file(fs, path, mode):
    mode = common._parse_mode(mode)

    try:
        return io.open(str(path), mode.io_open_string())
    except (IOError, OSError) as error:
        if error.errno == exceptions.FileNotFound.errno:
            raise exceptions.FileNotFound(path)
        elif error.errno == exceptions.IsADirectory.errno:
            raise exceptions.IsADirectory(path)
        elif error.errno == exceptions.SymbolicLoop.errno:
            raise exceptions.SymbolicLoop(path)
        raise


def _remove_file(fs, path):
    try:
        os.remove(str(path))
    except (IOError, OSError) as error:
        if error.errno == exceptions.FileNotFound.errno:
            raise exceptions.FileNotFound(path)
        elif error.errno == exceptions.PermissionError.errno:
            raise exceptions.PermissionError(path)
        raise


def _create_directory(fs, path):
    try:
        os.mkdir(str(path))
    except (IOError, OSError) as error:
        if error.errno == exceptions.FileNotFound.errno:
            raise exceptions.FileNotFound(path.parent())
        elif error.errno == exceptions.FileExists.errno:
            raise exceptions.FileExists(path)
        raise


def _list_directory(fs, path):
    try:
        return os.listdir(str(path))
    except (IOError, OSError) as error:
        if error.errno == exceptions.FileNotFound.errno:
            raise exceptions.FileNotFound(path)
        elif error.errno == exceptions.NotADirectory.errno:
            raise exceptions.NotADirectory(path)
        raise


def _remove_empty_directory(fs, path):
    try:
        os.rmdir(str(path))
    except (IOError, OSError) as error:
        if error.errno == exceptions.DirectoryNotEmpty.errno:
            raise exceptions.DirectoryNotEmpty(path)
        elif error.errno == exceptions.FileNotFound.errno:
            raise exceptions.FileNotFound(path)
        elif error.errno == exceptions.NotADirectory.errno:
            raise exceptions.NotADirectory(path)
        raise


def _link(fs, source, to):
    try:
        os.symlink(str(source), str(to))
    except (IOError, OSError) as error:
        if error.errno == exceptions.FileNotFound.errno:
            raise exceptions.FileNotFound(to.parent())
        elif error.errno == exceptions.NotADirectory.errno:
            raise exceptions.NotADirectory(to.parent())
        elif error.errno == exceptions.FileExists.errno:
            raise exceptions.FileExists(to)
        raise


def _readlink(fs, path):
    try:
        value = os.readlink(str(path))
    except (IOError, OSError) as error:
        if error.errno == exceptions.FileNotFound.errno:
            raise exceptions.FileNotFound(path)
        elif error.errno == exceptions.NotASymlink.errno:
            raise exceptions.NotASymlink(path)
        raise
    else:
        return Path.from_string(value)


FS = common.create(
    name="NativeFS",

    create_file=_create_file,
    open_file=_open_file,
    remove_file=_remove_file,

    create_directory=_create_directory,
    list_directory=_list_directory,
    remove_empty_directory=_remove_empty_directory,
    temporary_directory=lambda fs: Path.from_string(tempfile.mkdtemp()),

    link=_link,
    readlink=_readlink,

    exists=lambda fs, path: os.path.exists(str(path)),
    is_dir=lambda fs, path: os.path.isdir(str(path)),
    is_file=lambda fs, path: os.path.isfile(str(path)),
    is_link=lambda fs, path: os.path.islink(str(path)),
)
