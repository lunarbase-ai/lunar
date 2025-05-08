import { ComponentDataType } from "@/models/component/ComponentModel";
import { LunarAgent, ReasoningType } from "../types";

export const grantFinderAgent: LunarAgent = {
  instruction: "Read the set of links from the Grant List KB and output a structured table of available research grants.",
  agentName: "Grant Finder Agent",
  agentDescription: "An agent that reads trusted sources to extract and list available research grants, outputting a structured summary for downstream use.",
  inputs: [
    {
      name: "Grant List KB",
      dataType: ComponentDataType.FILE,
    }
  ],
  reasoningChain: [
    {
      id: "1",
      reasoningType: ReasoningType.GettingTrustedSources,
      reasoningDescription: "Reading the set of links from the Grant List KB.",
      executionTime: 2,
      output: {
        type: ComponentDataType.TEXT,
        content: `FSRMM – Research Grants on Neuromuscular Diseases

Swissuniversities / ORD programme – Track A: Establish ORD practices

Swissuniversities / ORD programme – Track B: Contribute to ORD communities

Swissuniversities / ORD programme – Track C: Explore innovative ORD

Swiss Cancer Research Foundation – Research Grants

Swiss Cancer Research Foundation – Scientific‑Conference Grants

Swiss Cancer Research Foundation – National MD‑PhD Programme

Swiss Cancer Research Foundation – International Research Fellowships

NVIDIA – Applied Research Accelerator Program

SNSF – Project Funding

SNSF – Flexibility Grants (Supplementary measure)

SNSF – Mobility Grants (Supplementary measure)

SNSF – Ambizione

SNSF – Postdoc.Mobility

SNSF – Doc.CH

SNSF – PRomys (Promoting Young Researchers)

SNSF – Starting Grants

SNSF – Consolidator Grants

SNSF – Agora (science communication)

SNSF – IICT 2024 (Investigator‑Initiated Clinical Trials)

SNSF – NCCR 2025 Call (National Centres of Competence in Research)

BRIDGE – Proof‑of‑Concept Grants

SNSF / DFG – WEAVE Lead Agency Germany

SNSF & partners – Belmont Forum Africa Regional Call

SNSF & partners – JPIAMR AMR‑Interventions Call

SNSF & partners – JPND 2024 Neurodegenerative‑Disease Call

SAMS – Young Talents in Clinical Research (Starter / Project Grants)

SAMS – Swiss National MD‑PhD Scholarships

European Respiratory Society – Long‑Term Research Fellowships

European Respiratory Society – Short‑Term Research Fellowships

European Respiratory Society – Clinical‑Training Fellowships

European Respiratory Society – RESPIRE4 MSCA Postdoctoral Fellowships

AFM‑Téléthon – Research Grants

AFM‑Téléthon – Postdoctoral Fellowships

AFM‑Téléthon – Trampoline (early‑stage) Grants

Muscular Dystrophy Association – Research Grants

Muscular Dystrophy Association – Development Grants

Muscular Dystrophy Association – Clinical‑Trial Grants

Jain Foundation – Dysferlinopathy Research Grants

LGMD2I Research Fund – Research Grants

A Foundation Building Strength – Nemaline Myopathy Research Grants

Myotubular Trust – Myotubular/CNM Research Grants

Takeda Oncology – Health‑Equity‑in‑Cancer Community Grants

G.& J. Bangerter‑Rhyner Foundation – Medical Research Grants

Branco Weiss Fellowship – Society‑in‑Science Postdoctoral Fellowship

Helmut Horten Foundation – Young Investigator Grants

Helmut Horten Foundation – Consortium Projects for Clinical Translation

Prof. Dr. Max Cloëtta Foundation – Clinical Medicine Plus Scholarships

Prof. Dr. Max Cloëtta Foundation – Medical Research Positions

Radala Foundation – ALS Advanced Research Grants

Frick Foundation – Starting Grants in ALS Basic Research

Pfizer Research Prize (Swiss medical‑research awards)

B‑M Stiftung – Annual Research & Scholarship Call

Novartis FreeNovation – Topic‑Driven Research Grants

Novartis Foundation for Medical‑Biological Research – Research Project Grants

Novartis Foundation for Medical‑Biological Research – Research Fellowships

Novartis Foundation for Medical‑Biological Research – Young Investigator Grants

FARA – Graduate Student Fellowships

FARA – Postdoctoral Research Awards

FARA – Collaboration Grants

FARA – Kyle Bryant Translational Research Award

FARA – Keith Michael Habilitation Fellowship

FARA – AIM (Accessibility, Inclusion & Mentorship) Award

FARA – General Research Grants

Simons Foundation – Simons Fellows in Mathematics

SFARI – Pilot Awards

Simons Foundation – Targeted Grants in Mathematics & Physical Sciences

Simons Foundation – Targeted Grants to Institutes

SFARI – Linking Early Neurodevelopment to Neural‑Circuit Outcomes RFA

Climate Change AI – Innovation Grants

Bloomberg – Data‑Science Research Grant Program

Cooperative AI Foundation – Research Grants

Cooperative AI Foundation – PhD Fellowship
`,
      },
    },
    {
      id: "2",
      reasoningType: ReasoningType.InterpretingWebSources,
      reasoningDescription: "Reading HTML documents and converting them to text.",
      executionTime: 30,
      output: {
        type: ComponentDataType.TEXT,
        content: "",
      },
    },
    {
      id: "3",
      reasoningType: ReasoningType.ExtractingCriteria,
      reasoningDescription: "Finding main fields of interest: funder, funding range, submission date, target theme, main eligibility, specifics of the call.",
      executionTime: 30,
      output: {
        type: ComponentDataType.TEXT,
        content: "",
      },
    },
    {
      id: "4",
      reasoningType: ReasoningType.ExtractingCriteria,
      reasoningDescription: `
      Normalizing date formats …
Generating Short descriptions …
Adding a link to the call…
`,
      executionTime: 15,
      output: {
        type: ComponentDataType.TEXT,
        content: "",
      },
    },
    {
      id: "5",
      reasoningType: ReasoningType.BuildingReport,
      reasoningDescription: "Organizing HTML document.",
      executionTime: 2,
      output: {
        type: ComponentDataType.TEXT,
        content: "",
      },
    },
    {
      id: "6",
      reasoningType: ReasoningType.BuildingReport,
      reasoningDescription: "Publishing final report.",
      executionTime: 3,
      output: {
        type: ComponentDataType.TEXT,
        content: "Report available here",
      },
    }
  ],
  manualTime: 28800, // 8 hours in seconds
};
