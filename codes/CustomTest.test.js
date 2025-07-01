"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const Setting_1 = require("./Setting");
const BaseModel_1 = require("../BaseModel");
const shim_1 = require("../shim");
const markdownUtils_1 = require("../markdownUtils");
const test_utils_1 = require("../testing/test-utils");
const Folder_1 = require("./Folder");
const Note_1 = require("./Note");
const Tag_1 = require("./Tag");
const ItemChange_1 = require("./ItemChange");
const Resource_1 = require("./Resource");
const path_utils_1 = require("../path-utils");
const ArrayUtils = require("../ArrayUtils");
const errors_1 = require("../errors");
const SearchEngine_1 = require("../services/search/SearchEngine");
const trash_1 = require("../services/trash");
const getConflictFolderId_1 = require("./utils/getConflictFolderId");
async function allItems() {
    const folders = await Folder_1.default.all();
    const notes = await Note_1.default.all();
    return folders.concat(notes);
}
describe('models/Note', () => {
    beforeEach(async () => {
        await (0, test_utils_1.setupDatabaseAndSynchronizer)(1);
        await (0, test_utils_1.switchClient)(1);
    });
    // TC033 kaynak ve not kimliklerini bulunabilkcegini test eder
    it('should find resource and note IDs', (async () => {
        const folder1 = await Folder_1.default.save({ title: 'folder1' });
        const note1 = await Note_1.default.save({ title: 'ma note', parent_id: folder1.id });
        let note2 = await Note_1.default.save({ title: 'ma deuxième note', body: `Lien vers première note : ${Note_1.default.markdownTag(note1)}`, parent_id: folder1.id });
        let items = await Note_1.default.linkedItems(note2.body);
        expect(items.length).toBe(1);
        expect(items[0].id).toBe(note1.id);
        await shim_1.default.attachFileToNote(note2, `${test_utils_1.supportDir}/photo.jpg`);
        note2 = await Note_1.default.load(note2.id);
        items = await Note_1.default.linkedItems(note2.body);
        expect(items.length).toBe(2);
        expect(items[0].type_).toBe(BaseModel_1.default.TYPE_NOTE);
        expect(items[1].type_).toBe(BaseModel_1.default.TYPE_RESOURCE);
        const resource2 = await shim_1.default.createResourceFromPath(`${test_utils_1.supportDir}/photo.jpg`);
        const resource3 = await shim_1.default.createResourceFromPath(`${test_utils_1.supportDir}/photo.jpg`);
        note2.body += `<img alt="bla" src=":/${resource2.id}"/>`;
        note2.body += `<img src=':/${resource3.id}' />`;
        items = await Note_1.default.linkedItems(note2.body);
        expect(items.length).toBe(4);
    }));
    // TC034 birbirine bağlı itemlar bulunabilmeli
    it('should find linked items', (async () => {
        const testCases = [
            ['[](:/06894e83b8f84d3d8cbe0f1587f9e226)', ['06894e83b8f84d3d8cbe0f1587f9e226']],
            ['[](:/06894e83b8f84d3d8cbe0f1587f9e226) [](:/06894e83b8f84d3d8cbe0f1587f9e226)', ['06894e83b8f84d3d8cbe0f1587f9e226']],
            ['[](:/06894e83b8f84d3d8cbe0f1587f9e226) [](:/06894e83b8f84d3d8cbe0f1587f9e227)', ['06894e83b8f84d3d8cbe0f1587f9e226', '06894e83b8f84d3d8cbe0f1587f9e227']],
            ['[](:/06894e83b8f84d3d8cbe0f1587f9e226 "some title")', ['06894e83b8f84d3d8cbe0f1587f9e226']],
        ];
        for (let i = 0; i < testCases.length; i++) {
            const t = testCases[i];
            const input = t[0];
            const expected = t[1];
            const actual = Note_1.default.linkedItemIds(input);
            const contentEquals = ArrayUtils.contentEquals(actual, expected);
            expect(contentEquals).toBe(true);
        }
    }));
    // TC035 notların tipi değiştirilebilmeli
    it('should change the type of notes', (async () => {
        const folder1 = await Folder_1.default.save({ title: 'folder1' });
        let note1 = await Note_1.default.save({ title: 'ma note', parent_id: folder1.id });
        note1 = await Note_1.default.load(note1.id);
        let changedNote = Note_1.default.changeNoteType(note1, 'todo');
        expect(changedNote === note1).toBe(false);
        expect(!!changedNote.is_todo).toBe(true);
        await Note_1.default.save(changedNote);
        note1 = await Note_1.default.load(note1.id);
        changedNote = Note_1.default.changeNoteType(note1, 'todo');
        expect(changedNote === note1).toBe(true);
        expect(!!changedNote.is_todo).toBe(true);
        note1 = await Note_1.default.load(note1.id);
        changedNote = Note_1.default.changeNoteType(note1, 'note');
        expect(changedNote === note1).toBe(false);
        expect(!!changedNote.is_todo).toBe(false);
    }));
    // TC036 veriler bozulmadan json formatına serialize-deserialize yapılabilmeli
    it('should serialize and unserialize without modifying data', (async () => {
        const folder1 = await Folder_1.default.save({ title: 'folder1' });
        const testCases = [
            [{ title: '', body: 'Body and no title\nSecond line\nThird Line', parent_id: folder1.id },
                '', 'Body and no title\nSecond line\nThird Line'],
            [{ title: 'Note title', body: 'Body and title', parent_id: folder1.id },
                'Note title', 'Body and title'],
            [{ title: 'Title and no body', body: '', parent_id: folder1.id },
                'Title and no body', ''],
        ];
        for (let i = 0; i < testCases.length; i++) {
            const t = testCases[i];
            const input = t[0];
            const note1 = await Note_1.default.save(input);
            const serialized = await Note_1.default.serialize(note1);
            const unserialized = await Note_1.default.unserialize(serialized);
            expect(unserialized.title).toBe(input.title);
            expect(unserialized.body).toBe(input.body);
        }
    }));
    // TC037 not duplike olduysa üretilirken alanlar silinmeli
    it('should reset fields for a duplicate', (async () => {
        const folder1 = await Folder_1.default.save({ title: 'folder1' });
        const note1 = await Note_1.default.save({ title: 'note', parent_id: folder1.id });
        await (0, test_utils_1.msleep)(1);
        const duplicatedNote = await Note_1.default.duplicate(note1.id);
        expect(duplicatedNote !== note1).toBe(true);
        expect(duplicatedNote.created_time !== note1.created_time).toBe(true);
        expect(duplicatedNote.updated_time !== note1.updated_time).toBe(true);
        expect(duplicatedNote.user_created_time !== note1.user_created_time).toBe(true);
        expect(duplicatedNote.user_updated_time !== note1.user_updated_time).toBe(true);
    }));
    // TC038 birbirinden farklı tag'i bulunan notlar duplike olabilmeli
    it('should duplicate a note with tags', (async () => {
        const folder1 = await Folder_1.default.save({ title: 'folder1' });
        const tag1 = await Tag_1.default.save({ title: 'tag1' });
        const tag2 = await Tag_1.default.save({ title: 'tag2' });
        const originalNote = await Note_1.default.save({ title: 'originalNote', parent_id: folder1.id });
        await Tag_1.default.addNote(tag1.id, originalNote.id);
        await Tag_1.default.addNote(tag2.id, originalNote.id);
        const duplicatedNote = await Note_1.default.duplicate(originalNote.id);
        const duplicatedNoteTags = await Tag_1.default.tagsByNoteId(duplicatedNote.id);
        expect(duplicatedNoteTags.find(o => o.id === tag1.id)).toBeDefined();
        expect(duplicatedNoteTags.find(o => o.id === tag2.id)).toBeDefined();
        expect(duplicatedNoteTags.length).toBe(2);
    }));
    // TC039 bir not duplike edilirken o nota ait kaynaklar de duplike edilmeli
    it('should also duplicate resources when duplicating a note', (async () => {
        const folder = await Folder_1.default.save({ title: 'folder' });
        let note = await Note_1.default.save({ title: 'note', parent_id: folder.id });
        await shim_1.default.attachFileToNote(note, `${test_utils_1.supportDir}/photo.jpg`);
        const resource = (await Resource_1.default.all())[0];
        expect((await Resource_1.default.all()).length).toBe(1);
        const duplicatedNote = await Note_1.default.duplicate(note.id, { duplicateResources: true });
        const resources = await Resource_1.default.all();
        expect(resources.length).toBe(2);
        const duplicatedResource = resources.find(r => r.id !== resource.id);
        note = await Note_1.default.load(note.id);
        expect(note.body).toContain(resource.id);
        expect(duplicatedNote.body).toContain(duplicatedResource.id);
        expect(duplicatedResource.share_id).toBe('');
        expect(duplicatedResource.is_shared).toBe(0);
    }));
    // TC040 bir not yanlışlıkla diğer benzer not yerine silinmemeli
    it('should delete nothing', (async () => {
        const f1 = await Folder_1.default.save({ title: 'folder1' });
        const f2 = await Folder_1.default.save({ title: 'folder2', parent_id: f1.id });
        const f3 = await Folder_1.default.save({ title: 'folder3', parent_id: f2.id });
        const f4 = await Folder_1.default.save({ title: 'folder4', parent_id: f1.id });
        const noOfNotes = 20;
        await (0, test_utils_1.createNTestNotes)(noOfNotes, f1, null, 'note1');
        await (0, test_utils_1.createNTestNotes)(noOfNotes, f2, null, 'note2');
        await (0, test_utils_1.createNTestNotes)(noOfNotes, f3, null, 'note3');
        await (0, test_utils_1.createNTestNotes)(noOfNotes, f4, null, 'note4');
        const beforeDelete = await allItems();
        await Note_1.default.batchDelete([]);
        const afterDelete = await allItems();
        expect((0, test_utils_1.sortedIds)(afterDelete)).toEqual((0, test_utils_1.sortedIds)(beforeDelete));
    }));
    // TC041 conflict varsa dosyaya taşıma işlemi yapmamalı (move işlemi)
    it('should not move to conflict folder', (async () => {
        const folder1 = await Folder_1.default.save({ title: 'Folder' });
        const folder2 = await Folder_1.default.save({ title: Folder_1.default.conflictFolderTitle(), id: Folder_1.default.conflictFolderId() });
        const note1 = await Note_1.default.save({ title: 'note', parent_id: folder1.id });
        const hasThrown = await (0, test_utils_1.checkThrowAsync)(async () => await Folder_1.default.moveToFolder(note1.id, folder2.id));
        expect(hasThrown).toBe(true);
        const note = await Note_1.default.load(note1.id);
        expect(note.parent_id).toEqual(folder1.id);
    }));
    // TC042 conflict varsa dosyaya taşıma işlemi yapmamalı (copy - ana kaynağı silmez)
    it('should not copy to conflict folder', (async () => {
        const folder1 = await Folder_1.default.save({ title: 'Folder' });
        const folder2 = await Folder_1.default.save({ title: Folder_1.default.conflictFolderTitle(), id: Folder_1.default.conflictFolderId() });
        const note1 = await Note_1.default.save({ title: 'note', parent_id: folder1.id });
        const hasThrown = await (0, test_utils_1.checkThrowAsync)(async () => await Note_1.default.copyToFolder(note1.id, folder2.id));
        expect(hasThrown).toBe(true);
    }));
    // TC043 lokal olarak verilen adresler internet adreslerine dönüşmemeli
    it('should convert resource paths from internal to external paths', (async () => {
        const resourceDirName = Setting_1.default.value('resourceDirName');
        const resourceDir = Setting_1.default.value('resourceDir');
        const r1 = await shim_1.default.createResourceFromPath(`${test_utils_1.supportDir}/photo.jpg`);
        const r2 = await shim_1.default.createResourceFromPath(`${test_utils_1.supportDir}/photo.jpg`);
        const r3 = await shim_1.default.createResourceFromPath(`${test_utils_1.supportDir}/welcome.pdf`);
        const note1 = await Note_1.default.save({ title: 'note1' });
        const t1 = r1.updated_time;
        const t2 = r2.updated_time;
        const resourceDirE = markdownUtils_1.default.escapeLinkUrl((0, path_utils_1.toForwardSlashes)(resourceDir));
        const fileProtocol = `file://${process.platform === 'win32' ? '/' : ''}`;
        const testCases = [
            [
                false,
                '',
                '',
            ],
            [
                true,
                '',
                '',
            ],
            [
                false,
                `![](:/${r1.id})`,
                `![](${resourceDirName}/${r1.id}.jpg)`,
            ],
            [
                false,
                `![](:/${r1.id}) ![](:/${r1.id}) ![](:/${r2.id})`,
                `![](${resourceDirName}/${r1.id}.jpg) ![](${resourceDirName}/${r1.id}.jpg) ![](${resourceDirName}/${r2.id}.jpg)`,
            ],
            [
                true,
                `![](:/${r1.id})`,
                `![](${fileProtocol}${resourceDirE}/${r1.id}.jpg?t=${t1})`,
            ],
            [
                true,
                `![](:/${r1.id}) ![](:/${r1.id}) ![](:/${r2.id})`,
                `![](${fileProtocol}${resourceDirE}/${r1.id}.jpg?t=${t1}) ![](${fileProtocol}${resourceDirE}/${r1.id}.jpg?t=${t1}) ![](${fileProtocol}${resourceDirE}/${r2.id}.jpg?t=${t2})`,
            ],
            [
                true,
                `![](:/${r3.id})`,
                `![](${fileProtocol}${resourceDirE}/${r3.id}.pdf)`,
            ],
        ];
        for (const testCase of testCases) {
            const [useAbsolutePaths, input, expected] = testCase;
            const internalToExternal = await Note_1.default.replaceResourceInternalToExternalLinks(input, { useAbsolutePaths });
            expect(internalToExternal).toBe(expected);
            const externalToInternal = await Note_1.default.replaceResourceExternalToInternalLinks(internalToExternal, { useAbsolutePaths });
            expect(externalToInternal).toBe(input);
        }
        {
            const result = await Note_1.default.replaceResourceExternalToInternalLinks(`[](joplin://${note1.id})`);
            expect(result).toBe(`[](:/${note1.id})`);
        }
        {
            const noChangeInput = `[docs](file:///c:/foo/${resourceDirName}/docs)`;
            const result = await Note_1.default.replaceResourceExternalToInternalLinks(noChangeInput, { useAbsolutePaths: false });
            expect(result).toBe(noChangeInput);
        }
    }));
    // TC044 notlar oluşturulduğu halde bile doğal olarak alfebatik olarak sıralanmalı
    it('should perform natural sorting', (async () => {
        const folder1 = await Folder_1.default.save({});
        const sortedNotes = await Note_1.default.previews(folder1.id, {
            fields: ['id', 'title'],
            order: [{ by: 'title', dir: 'ASC' }],
        });
        expect(sortedNotes.length).toBe(0);
        const note0 = await Note_1.default.save({ title: 'A3', parent_id: folder1.id, is_todo: 0 });
        const note1 = await Note_1.default.save({ title: 'A20', parent_id: folder1.id, is_todo: 0 });
        const note2 = await Note_1.default.save({ title: 'A100', parent_id: folder1.id, is_todo: 0 });
        const note3 = await Note_1.default.save({ title: 'égalité', parent_id: folder1.id, is_todo: 0 });
        const note4 = await Note_1.default.save({ title: 'z', parent_id: folder1.id, is_todo: 0 });
        const sortedNotes2 = await Note_1.default.previews(folder1.id, {
            fields: ['id', 'title'],
            order: [{ by: 'title', dir: 'ASC' }],
        });
        expect(sortedNotes2.length).toBe(5);
        expect(sortedNotes2[0].id).toBe(note0.id);
        expect(sortedNotes2[1].id).toBe(note1.id);
        expect(sortedNotes2[2].id).toBe(note2.id);
        expect(sortedNotes2[3].id).toBe(note3.id);
        expect(sortedNotes2[4].id).toBe(note4.id);
        const todo3 = Note_1.default.changeNoteType(note3, 'todo');
        const todo4 = Note_1.default.changeNoteType(note4, 'todo');
        await Note_1.default.save(todo3);
        await Note_1.default.save(todo4);
        const sortedNotes3 = await Note_1.default.previews(folder1.id, {
            fields: ['id', 'title'],
            order: [{ by: 'title', dir: 'ASC' }],
            uncompletedTodosOnTop: true,
        });
        expect(sortedNotes3.length).toBe(5);
        expect(sortedNotes3[0].id).toBe(note3.id);
        expect(sortedNotes3[1].id).toBe(note4.id);
        expect(sortedNotes3[2].id).toBe(note0.id);
        expect(sortedNotes3[3].id).toBe(note1.id);
        expect(sortedNotes3[4].id).toBe(note2.id);
    }));
    // TC045 çakışma olduğunda uyarı vermeli
    it('should create a conflict note', async () => {
        const folder = await Folder_1.default.save({ title: 'Source Folder' });
        const origNote = await Note_1.default.save({ title: 'note', parent_id: folder.id, share_id: 'SHARE', is_shared: 1 });
        const conflictedNote = await Note_1.default.createConflictNote(origNote, ItemChange_1.default.SOURCE_SYNC);
        expect(conflictedNote.is_conflict).toBe(1);
        expect(conflictedNote.conflict_original_id).toBe(origNote.id);
        expect(conflictedNote.parent_id).toBe(folder.id);
        expect(conflictedNote.is_shared).toBeUndefined();
        expect(conflictedNote.share_id).toBe('');
    });
    // TC046 onay verilmesi halinde çakışan not yeni klasöre taşınmalı ve o klasördeki eski not silinmeli
    it('should copy conflicted note to target folder and cancel conflict', (async () => {
        const srcfolder = await Folder_1.default.save({ title: 'Source Folder' });
        const targetfolder = await Folder_1.default.save({ title: 'Target Folder' });
        const note1 = await Note_1.default.save({ title: 'note', parent_id: srcfolder.id });
        const conflictedNote = await Note_1.default.createConflictNote(note1, ItemChange_1.default.SOURCE_SYNC);
        const note2 = await Note_1.default.copyToFolder(conflictedNote.id, targetfolder.id);
        expect(note2.id === conflictedNote.id).toBe(false);
        expect(note2.title).toBe(conflictedNote.title);
        expect(note2.is_conflict).toBe(0);
        expect(note2.conflict_original_id).toBe('');
        expect(note2.parent_id).toBe(targetfolder.id);
    }));
});