(* ========= YAML/JSON loader ========= *)
ClearAll[LoadParams];

Options[LoadParams] = {"Prefer" -> Automatic};  (* "YAML"|"JSON"|Automatic *)

LoadParams[path_, OptionsPattern[]] := Module[
  {ext = ToLowerCase@FileExtension[path], prefer = OptionValue["Prefer"], data, tryWL, tryPy},
  
  tryWL[f_, fmt_] := Quiet @ Check[Import[f, fmt], $Failed];
  
  tryPy[f_] := Module[{ev = FindExternalEvaluators["Python"], sess, txt, res},
    If[ev === {} , Return[$Failed]];
    sess = StartExternalSession[First@ev];
    res = ExternalEvaluate[sess, "
import json, sys
try:
    import yaml
except ImportError:
    sys.exit('no_yaml')
import io, os
p = r'''" + f + "''' 
with io.open(p, 'r', encoding='utf-8') as fp:
    d = yaml.safe_load(fp)
print(json.dumps(d))
"];
    KillExternalSession[sess];
    If[res === "no_yaml", Return[$Failed]];
    ImportString[res, "RawJSON"]
  ];
  
  Which[
    (* explicit preference *)
    prefer === "JSON" || ext === "json", Import[path, "RawJSON"],
    prefer === "YAML" || ext === "yaml" || ext === "yml",
      With[{r1 = tryWL[path, "YAML"]}, If[r1 =!= $Failed, r1, tryPy[path]]],
    True,  (* Automatic by extension *)
      Switch[ext,
        "json", Import[path, "RawJSON"],
        "yaml" | "yml", With[{r1 = tryWL[path, "YAML"]}, If[r1 =!= $Failed, r1, tryPy[path]]],
        _, Message[LoadParams::ext, ext]; $Failed
      ]
  ]
];

LoadParams::ext = "Невідоме розширення: `1`.";

proj    = NotebookDirectory[] /. $Failed :> DirectoryName[$InputFileName];
root    = FileNameJoin[{proj, ".."}];

(* allow both JSON and YAML *)
paramFN = If[FileExistsQ@FileNameJoin[{root, "params", "pack.yaml"}],
             FileNameJoin[{root, "params", "pack.yaml"}],
             FileNameJoin[{root, "params", "pack.json"}]
           ];

outDir  = FileNameJoin[{root, "out", "wl"}];
If[!DirectoryQ[outDir], CreateDirectory[outDir, CreateIntermediateDirectories->True]];

params = LoadParams[paramFN];
If[params === $Failed, Print["⛘ Не вдалося завантажити параметри: ", paramFN]; Abort[]];

SeedRandom[Lookup[params, "seed", 1337]];
{w, h} = Lookup[params, "image_size", {1280, 720}];

(* main logic placeholder *)
Print["Loaded parameters: ", params];
