# Z3 Asset Map

A project to rebuild Z3's internal file structure, so that Escartem's [AnimeStudio](https://github.com/Escartem/AnimeStudio) can extract assets "byContainer".

Unlike a specific turn-based game, which has the internal containers kept within the blocks, meaning there's no real need for an Asset-Index, Z3 instead hashes the containers with xxhash64, which is what leads to AnimeStudio just dumping thousands of files into folders named by the typeID of the file (Texture2D/Mesh/Animator, etc).

I wanted to be able to find assets, especially Texture2D, more easily by having them sorted, which led me down this particular rabbit-hole. This method also allows correct extraction of duplicates, without getting swamped with 30 files that are all called the same thing and simply appended with (0), (1), (2).

## Generation

- Used AnimeStudio to generate a full assets_map of the game.
- Extracted all valid containerIDs from the assets_map.
- Extracted various lists of files based on typeID from the assets_map.
- Extracted all visible strings from /Data and /FileCFG using a specific data repository.
- Extracted all strings from MonoBehaviours using my modified fork of AnimeStudio.
- Ran trillions of potential path/file combinations through a brute-forcing script.
- Ran the game with Frida hooking into certain RVAs that deal with hashing and texture loading.

## Progress

Some reported numbers from the AssetMap might be a bit skewed, due to the inclusion of files like resources.assets.

| typeID        | File Types                                                                                                             | AssetMap Total | Remaining | % Done |
| ------------- | ---------------------------------------------------------------------------------------------------------------------- | -------------- | --------- | ------ |
| AnimationClip | .fbx, .anim                                                                                                            | 27,171         | 10,415    | 61.67% |
| Animator      | .fbx, .prefab                                                                                                          | 5,749          | 2,533     | 55.95% |
| Material      | .mat                                                                                                                   | 41,688         | 22,109    | 46.95% |
| Mesh          | .fbx, .mesh                                                                                                            | 97,561         | 67,698    | 30.61% |
| MonoBehaviour | .asset, .playable, .prefab                                                                                             | 95,638         | 29,985    | 68.65% |
| TextAsset     | .bytes, .csv, .html, .json, .txt                                                                                       | 14,883         | 4,530     | 69.57% |
| Texture2D     | .jpg, .png, .psd, .tga                                                                                                 | 49,658         | 11,685    | 76.47% |
| TOTAL         | .anim, .asset, .bytes, .csv, .fbx, .html, .jpg, .json, .mat, .mesh,<br />.playable, .png, .prefab, .psd, .tga, .txt | 332,348        | 148,955   | 55.19% |

### AssetMap

The values in () are for files with duped file extensions (.asset.asset, .png.png, .tga.tga).

| Extension       | Amount      |
| --------------- | ----------- |
| .anim           | 1,176       |
| .asset          | 49,993 (+1) |
| .bytes          | 9,452       |
| .csv            | 1           |
| .fbx            | 38,426      |
| .html           | 3           |
| .jpg            | 14          |
| .json           | 556         |
| .mat            | 19,408      |
| .mesh           | 5,274       |
| .otf            | 7           |
| .playable       | 310         |
| .png            | 18,691 (+6) |
| .prefab         | 31,572      |
| .psd            | 1,290       |
| .shadervariants | 177         |
| .tga            | 18,748 (+2) |
| .txt            | 385         |
| TOTAL           | 195,483     |

## Issues

As I only have a couple of usable RVAs to try and hook into, many files simply get read as .prefab files and paths, without showing where the actual files used are streamed from. Likewise, brute-forcing, as per its nature, is incredibly hit-or-miss;

I have been unable to find the paths for these files:

| Asset Type                                  | Amount |
| ------------------------------------------- | ------ |
| Story Comics                                | ~1,700 |
| Weapon Textures                             | ~300   |
| Various EFF/VX/Mask/HLOD textures/materials | 2000+  |
| Agent Mindscape Images                      | ~150   |
| All Live2D spines/atlases/skeletons         | A lot  |

## Credits

* Escartem: Anime studio and helping with Monos and fixes.
* yarik0chka: Some files.
* Dimbreath: Z3 Data
* Hrothgar: Assisting where possible.
* undefined9071: Help with Monos.
