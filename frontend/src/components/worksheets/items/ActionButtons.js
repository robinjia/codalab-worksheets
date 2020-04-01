// @flow
import * as React from 'react';
import Button from '@material-ui/core/Button';
import { withStyles } from '@material-ui/core/styles';
import RunIcon from '@material-ui/icons/PlayCircleOutline';
import UploadIcon from '@material-ui/icons/CloudUploadOutlined';
import AddIcon from '@material-ui/icons/AddBoxOutlined';
import NoteAddIcon from '@material-ui/icons/NoteAdd';
import BundleBulkActionMenu from '../BundleBulkActionMenu';
import Tooltip from '@material-ui/core/Tooltip';
import IconButton from '@material-ui/core/IconButton';

class ActionButtons extends React.Component<{
    classes: {},
    onShowNewRun: () => void,
    onShowNewText: () => void,
}> {
    render() {
        const {
            classes,
            onShowNewRun,
            onShowNewText,
            handleSelectedBundleCommand,
            showBundleOperationButtons,
            toggleCmdDialog,
            toggleCmdDialogNoEvent,
            info,
            pasteToWorksheet,
        } = this.props;
        let editPermission = info && info.edit_permission;
        return (
            <div
                onMouseMove={(ev) => {
                    ev.stopPropagation();
                }}
            >
                {' '}
                {!showBundleOperationButtons ? (
                    <Button
                        size='small'
                        color='inherit'
                        aria-label='Add Text'
                        onClick={onShowNewText}
                        disabled={!editPermission}
                    >
                        <AddIcon className={classes.buttonIcon} />
                        Text
                    </Button>
                ) : null}
                {!showBundleOperationButtons ? (
                    <Button
                        size='small'
                        color='inherit'
                        aria-label='Add New Upload'
                        className={classes.uploadButton}
                        disabled={!editPermission}
                    >
                        <label className={classes.uploadLabel} for='codalab-file-upload-input'>
                            <UploadIcon className={classes.buttonIcon} />
                            Upload
                        </label>
                    </Button>
                ) : null}
                {!showBundleOperationButtons ? (
                    <Button
                        size='small'
                        color='inherit'
                        aria-label='Add New Run'
                        onClick={onShowNewRun}
                        disabled={!editPermission}
                    >
                        <RunIcon className={classes.buttonIcon} />
                        Run
                    </Button>
                ) : null}
                {showBundleOperationButtons ? (
                    <BundleBulkActionMenu
                        handleSelectedBundleCommand={handleSelectedBundleCommand}
                        toggleCmdDialog={toggleCmdDialog}
                        toggleCmdDialogNoEvent={toggleCmdDialogNoEvent}
                    />
                ) : null}
                <Tooltip title='Paste text or uuids to this worksheet'>
                    <Button
                        size='small'
                        color='inherit'
                        aria-label='Paste'
                        onClick={pasteToWorksheet}
                        disabled={!editPermission}
                        id='paste-button'
                    >
                        <NoteAddIcon className={classes.buttonIcon} />
                        Paste
                    </Button>
                </Tooltip>
            </div>
        );
    }
}

const styles = (theme) => ({
    container: {
        position: 'relative',
        marginBottom: 20,
        zIndex: 5,
    },
    main: {
        zIndex: 10,
        border: `2px solid transparent`,
        '&:hover': {
            backgroundColor: theme.color.grey.lightest,
            border: `2px solid ${theme.color.grey.base}`,
        },
    },
    buttonIcon: {
        marginRight: theme.spacing.large,
    },
    uploadButton: {
        padding: 0,
    },
    uploadLabel: {
        width: '100%',
        display: 'inherit',
        padding: '4px 8px',
        marginBottom: 0,
        fontWeight: 'inherit',
        cursor: 'inherit',
    },
});

export default withStyles(styles)(ActionButtons);
